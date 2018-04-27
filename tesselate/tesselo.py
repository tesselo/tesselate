import os
import urllib
from collections import OrderedDict
import logging


from tesselate.client import Client
import requests
from django.conf import settings
from django.contrib.gis.gdal import DataSource, GDALRaster, OGRGeometry
from raster.tiles.const import WEB_MERCATOR_SRID, WEB_MERCATOR_TILESIZE
from raster.tiles.utils import tile_bounds, tile_index_range, tile_scale

# Datatype constants.
RASTER_DATATYPE = 'float32'
RASTER_DATATYPE_GDAL = 6
LOOKUP = {
    'B1': 'B01.jp2',
    'B2': 'B02.jp2',
    'B3': 'B03.jp2',
    'B4': 'B04.jp2',
    'B5': 'B05.jp2',
    'B6': 'B06.jp2',
    'B7': 'B07.jp2',
    'B8': 'B08.jp2',
    'B8A': 'B8A.jp2',
    'B9': 'B09.jp2',
    'B10': 'B10.jp2',
    'B11': 'B11.jp2',
    'B12': 'B12.jp2',
}


class Tesselo(object):


    def __init__(self, token=None):
        self.client = Client()

        # For the raster tilesize function.
        try:
            settings.configure()
        except:
            pass

    def area(self, pk=None, **filters):
        return self.client.get_rest('aggregationlayer', pk=pk, **filters)

    def composite(self, pk=None, **filters):
        return self.client.get_rest('composite', pk=pk, **filters)

    def formula(self, pk=None, **filters):
        return self.client.get_rest('formula', pk=pk, **filters)

    def export(self, area, composite, formula, tilez=14):
        logging.info('Processing "{}" over "{}" for "{}"'.format(formula['name'], area['name'], composite['name']))

        # Convert bbox to web mercator.
        geom = OGRGeometry.from_bbox(area['extent'])
        geom.srid = 4326
        geom.transform(WEB_MERCATOR_SRID)
        extent = geom.extent

        # Compute target index range.
        index_range = tile_index_range(extent, tilez)

        # Create target raster.
        target_name = formula['acronym'].lower()
        target = self._create_target_raster(extent, target_name, '/tmp/', tilez)

        for tilex in range(index_range[0], index_range[2] + 1):
            for tiley in range(index_range[1], index_range[3] + 1):

                if formula['acronym'] == 'RGB':
                    self._process_rgb(tilez, tilex, tiley, index_range, formula, composite, target)

                else:
                    self._process_algebra(tilez, tilex, tiley, index_range, formula, composite, target)

    def _process_rgb(self, tilez, tilex, tiley, index_range, formula, composite, target):
        # Construct url.
        url = 'algebra/{}/{}/{}.png?layers=r={},g={},b={}&scale=0,4e3&alpha&enhance_brightness=1.6&enhance_sharpness=1.2&enhance_color=1.2&enhance_contrast=1.1'.format(
            tilez,
            tilex,
            tiley,
            composite['rasterlayer_lookup']['B04.jp2'],
            composite['rasterlayer_lookup']['B03.jp2'],
            composite['rasterlayer_lookup']['B02.jp2'],
        )
        # Get data.
        data = self.client.get(url, json_response=False)
        # Open response as GDALRaster.
        with open('/tmp/bla.png', 'wb') as f:
            f.write(data)
        rst = GDALRaster('/tmp/bla.png')
        # Open as GDAL raster and print to screen.
        xoffset = (tilex - index_range[0]) * WEB_MERCATOR_TILESIZE
        yoffset = (tiley - index_range[1]) * WEB_MERCATOR_TILESIZE
        # Write data to target.
        for band_idx in range(3):
            target.bands[band_idx].data(
                rst.bands[band_idx].data().astype('uint8'),#RASTER_DATATYPE),
                size=(WEB_MERCATOR_TILESIZE, WEB_MERCATOR_TILESIZE),
                offset=(xoffset, yoffset),
            )

    def _process_algebra(self, tilez, tilex, tiley, index_range, formula, composite, target):
        # Construct layers lookup parameter.
        layers = []
        for key, layer in LOOKUP.items():
            if key in formula['formula']:
                layers.append('{}={}'.format(key, composite['rasterlayer_lookup'][layer]))
        layers = ','.join(layers)
        # Encode formula.
        formula_encoded = urllib.parse.quote(formula['formula'].replace(' ', ''), safe='()/')
        # Consturct url.
        url = 'algebra/{}/{}/{}.tif?formula={}&layers={}'.format(tilez, tilex, tiley, formula_encoded, layers)
        # Retrieve data.
        data = self.client.get(url, json_response=False)
        # Open response as GDALRaster.
        rst = GDALRaster(data)
        # Open as GDAL raster and print to screen.
        xoffset = (tilex - index_range[0]) * WEB_MERCATOR_TILESIZE
        yoffset = (tiley - index_range[1]) * WEB_MERCATOR_TILESIZE
        # Write data
        target.bands[0].data(
            rst.bands[0].data().astype(RASTER_DATATYPE),
            size=(WEB_MERCATOR_TILESIZE, WEB_MERCATOR_TILESIZE),
            offset=(xoffset, yoffset),
        )

    def _create_target_raster(self, bbox, target_name, base_path, zoom):
        """
        Create empty target rasters on disk for all bands. The empty rasters
        will be populated with tile data in a second step.
        """
        origin, width, height, scale = self._get_geotransform(bbox, zoom)

        # Construct bands.
        if target_name.lower() == 'rgb':
            bands = [
                {'data': [0], 'size': (1, 1), 'nodata_value': 0},
                {'data': [0], 'size': (1, 1), 'nodata_value': 0},
                {'data': [0], 'size': (1, 1), 'nodata_value': 0},
            ]
            dtype = 1
        else:
            bands = [{'data': [0], 'size': (1, 1), 'nodata_value': 0}]
            dtype = RASTER_DATATYPE_GDAL

        return GDALRaster({
            'name': os.path.join(base_path, '{}.tif'.format(target_name)),
            'driver': 'tif',
            'datatype': dtype,
            'origin': origin,
            'width': width,
            'height': height,
            'srid': WEB_MERCATOR_SRID,
            'scale': (scale, -scale),
            'bands': bands,
            'papsz_options': {
                'compress': 'packbits',
            }
        })

    def _get_geotransform(self, bbox, zoom):
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
