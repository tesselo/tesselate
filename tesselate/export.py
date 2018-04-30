import logging
import os
import tempfile

from raster.tiles.const import WEB_MERCATOR_SRID, WEB_MERCATOR_TILESIZE
from raster.tiles.utils import tile_bounds, tile_index_range, tile_scale

from django.contrib.gis.gdal import GDALRaster, OGRGeometry
from tesselate import const, tiles


def export(client, region, composite, formula, file_path, tilez=14):
    logging.info('Processing "{}" over "{}" for "{}"'.format(formula['name'], region['name'], composite['name']))

    # Convert bbox to web mercator.
    geom = OGRGeometry.from_bbox(region['extent'])
    geom.srid = 4326
    geom.transform(WEB_MERCATOR_SRID)
    extent = geom.extent

    # Compute target index range.
    index_range = tile_index_range(extent, tilez)

    # Check if this is an rgb raster.
    rgb = formula['acronym'].lower() == 'rgb'

    # Create target raster.
    target = _create_target_raster(extent, file_path, tilez, rgb)

    for tilex in range(index_range[0], index_range[2] + 1):
        for tiley in range(index_range[1], index_range[3] + 1):

            if formula['acronym'] == 'RGB':
                _process_rgb(client, tilez, tilex, tiley, index_range, formula, composite, target)

            else:
                _process_algebra(client, tilez, tilex, tiley, index_range, formula, composite, target)


def _process_rgb(client, tilez, tilex, tiley, index_range, formula, composite, target):
    # Compute pixel offxet for this tile.
    xoffset = (tilex - index_range[0]) * WEB_MERCATOR_TILESIZE
    yoffset = (tiley - index_range[1]) * WEB_MERCATOR_TILESIZE
    # Get tile.
    data = tiles.rgb(client, tilez, tilex, tiley, composite)
    # Open response as GDALRaster. The tempfile workaround is because the png
    # buffer itself is not readable by GDALRaster.
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(data)
        rst = GDALRaster(tmp.name)
        # Write data to target.
        for band_idx in range(3):
            target.bands[band_idx].data(
                rst.bands[band_idx].data().astype('uint8'),  # TODO: Maybe use const.RASTER_DATATYPE
                size=(WEB_MERCATOR_TILESIZE, WEB_MERCATOR_TILESIZE),
                offset=(xoffset, yoffset),
            )


def _process_algebra(client, tilez, tilex, tiley, index_range, formula, composite, target):
    # Fetch tile.
    data = tiles.algebra(client, tilez, tilex, tiley, composite, formula)
    # Open response as GDALRaster.
    rst = GDALRaster(data)
    # Compute offset for this tile within parent raster.
    xoffset = (tilex - index_range[0]) * WEB_MERCATOR_TILESIZE
    yoffset = (tiley - index_range[1]) * WEB_MERCATOR_TILESIZE
    # Write data
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

    # Construct bands.
    if rgb:
        bands = [
            {'data': [0], 'size': (1, 1), 'nodata_value': 0},
            {'data': [0], 'size': (1, 1), 'nodata_value': 0},
            {'data': [0], 'size': (1, 1), 'nodata_value': 0},
        ]
        dtype = 1
    else:
        bands = [{'data': [0], 'size': (1, 1), 'nodata_value': 0}]
        dtype = const.RASTER_DATATYPE_GDAL

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
        'papsz_options': {
            'compress': 'deflate',
        }
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
