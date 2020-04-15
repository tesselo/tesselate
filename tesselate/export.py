import logging
import tempfile
import uuid

import numpy
from django.contrib.gis.gdal import GDALException, GDALRaster, OGRGeometry
from raster.rasterize import rasterize
from raster.tiles.const import WEB_MERCATOR_SRID, WEB_MERCATOR_TILESIZE
from raster.tiles.utils import tile_bounds, tile_index_range, tile_scale

from tesselate import const, tiles
from tesselate.utils import populate_aggregation_areas


def export(client, region, composite, formula, file_path=None, zoom=14, clip_to_geom=False, all_touched=False):
    logging.info('Processing aggregation{} "{}" over "{}" for "{}" at zoom "{}"'.format(
        'layer' if 'aggregationareas' in region else 'area',
        formula['name'],
        region['name'],
        composite['name'],
        zoom,
    ))

    # Ensure bbox is a Geom in web mercator.
    geom = OGRGeometry.from_bbox(region['extent'])
    geom.srid = 4326
    geom.transform(WEB_MERCATOR_SRID)
    extent = geom.extent

    # Compute target index range.
    index_range = tile_index_range(extent, zoom)

    # Check if this is an rgb raster.
    rgb = formula['acronym'].lower() == 'rgb'

    # Create target raster.
    target = _create_target_raster(extent, file_path, zoom, rgb)

    # Compute nr of tiles to process.
    tile_count = (index_range[2] - index_range[0] + 1) * (index_range[3] - index_range[1] + 1)
    counter = 0
    logging.info('Found {} tiles to process for export.'.format(tile_count))

    # Get and write tiles.
    for tilex in range(index_range[0], index_range[2] + 1):
        for tiley in range(index_range[1], index_range[3] + 1):
            # Log progress.
            if counter % 100 == 0:
                logging.info('Processed {}/{} tiles.'.format(counter, tile_count))
            counter += 1

            if formula['acronym'] == 'RGB':
                _process_rgb(client, zoom, tilex, tiley, index_range, formula, composite, target)
            else:
                _process_algebra(client, zoom, tilex, tiley, index_range, formula, composite, target)

    # Clip to geometry.
    if clip_to_geom:
        _clip_to_geom(client, target, region, all_touched=all_touched)

    # Return numpy array if no target file path has been specified.
    if target.name.startswith('/vsimem'):
        return numpy.array([band.data() for band in target.bands])


def _process_rgb(client, zoom, tilex, tiley, index_range, formula, composite, target):
    if not target:
        raise ValueError('Target raster path must be specified for RGB exports.')
    # Compute pixel offxet for this tile.
    xoffset = (tilex - index_range[0]) * WEB_MERCATOR_TILESIZE
    yoffset = (tiley - index_range[1]) * WEB_MERCATOR_TILESIZE
    # Get tile.
    data = tiles.rgb(client, zoom, tilex, tiley, composite)
    # Open response as GDALRaster. The tempfile workaround is because the png
    # buffer itself is not readable by GDALRaster.
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(data)
        try:
            rst = GDALRaster(tmp.name)
        except GDALException:
            return
        # Write data to target.
        for band_idx in range(3):
            target.bands[band_idx].data(
                rst.bands[band_idx].data().astype('uint8'),  # TODO: Maybe use const.RASTER_DATATYPE
                size=(WEB_MERCATOR_TILESIZE, WEB_MERCATOR_TILESIZE),
                offset=(xoffset, yoffset),
            )


def _process_algebra(client, zoom, tilex, tiley, index_range, formula, composite, target):
    # Fetch tile.
    data = tiles.algebra(client, zoom, tilex, tiley, composite, formula)
    # Open response as GDALRaster.
    rst = GDALRaster(data)
    # Compute offset for this tile within parent raster.
    xoffset = (tilex - index_range[0]) * WEB_MERCATOR_TILESIZE
    yoffset = (tiley - index_range[1]) * WEB_MERCATOR_TILESIZE
    # Write data into raster.
    target.bands[0].data(
        rst.bands[0].data().astype(const.RASTER_DATATYPE),
        size=(WEB_MERCATOR_TILESIZE, WEB_MERCATOR_TILESIZE),
        offset=(xoffset, yoffset),
    )


def _create_target_raster(bbox, file_path, zoom, rgb=False):
    """
    Create empty target rasters on disk for all bands. The empty rasters
    will be populated with tile data in a second step.
    """
    origin, width, height, scale = _get_geotransform(bbox, zoom)
    logging.debug('Target geotransform {} {} {} {}.'.format(origin, width, height, scale))

    # Construct bands.
    if rgb:
        bands = [
            {'data': [0], 'size': (1, 1), 'nodata_value': None},
            {'data': [0], 'size': (1, 1), 'nodata_value': None},
            {'data': [0], 'size': (1, 1), 'nodata_value': None},
        ]
        dtype = 1
        papsz_options = {
            'compress': 'deflate',
            'bigtiff': 'yes',
        }
    else:
        bands = [{'data': [0], 'size': (1, 1), 'nodata_value': 0}]
        dtype = const.RASTER_DATATYPE_GDAL
        papsz_options = {
            'compress': 'deflate',
            'bigtiff': 'yes',
        }

    # Use vsi memory filesystem if no file path was provided.
    if not file_path:
        file_path = '/vsimem/{}'.format(uuid.uuid4())

    return GDALRaster({
        'name': file_path,
        'driver': 'tif',
        'datatype': dtype,
        'origin': origin,
        'width': width,
        'height': height,
        'srid': WEB_MERCATOR_SRID,
        'scale': (scale, -scale),
        'bands': bands,
        'papsz_options': papsz_options,
    })


def _get_geotransform(bbox, zoom):
    """
    Compute geotransform parameters for target rasters based on bbox and zoom.
    """
    if not isinstance(bbox, (tuple, list)):
        bbox = bbox.extent
    tile_range = tile_index_range(bbox, zoom)
    scale = tile_scale(zoom)
    bnds = tile_bounds(tile_range[0], tile_range[1], zoom)
    origin = (bnds[0], bnds[3])
    xlen = tile_range[2] - tile_range[0] + 1
    ylen = tile_range[3] - tile_range[1] + 1
    width = xlen * WEB_MERCATOR_TILESIZE
    height = ylen * WEB_MERCATOR_TILESIZE
    return origin, width, height, scale


def _clip_to_geom(client, result, region, all_touched=False):
    if 'aggregationareas' in region:
        # Collect geometries if this is an aggregationlayer.
        populate_aggregation_areas(client, region)
        geom = None
        geoms = [OGRGeometry(area['geom']) for area in region['aggregationareas']]
        geom = geoms.pop()
        for new_geom in geoms:
            geom = geom.union(new_geom)
    else:
        geom = OGRGeometry(region['geom'])

    # Rasterize the resulting geometry.
    geom_rst = rasterize(geom, result, all_touched=all_touched)
    geom_mask = geom_rst.bands[0].data() == 0
    # Use geom mask to change target data.
    for band in result.bands:
        band_data = band.data()
        band_data[geom_mask] = const.NODATA_VALUE
        band.data(band_data)
