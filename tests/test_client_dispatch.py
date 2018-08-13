import logging
import os
import unittest

import mock
from tests.utils import TesselateMockResponseBase

from tesselate import Tesselate

# Reduce log level during tests.
logging.getLogger().setLevel(logging.ERROR)


def mock_get_formula_list(session, url):

    class MockResponse(TesselateMockResponseBase):

        def json(self):
            return {
                'count': 1232,
                'next': 'https://tesselo.com/api/formula.json?page=5',
                'previous': 'https://tesselo.com/api/formula.json?page=3',
                'results': [
                    {'id': 36, 'name': 'Chlorophyll Index', 'acronym': 'CI', 'description': 'Chlorophyll Index', 'formula': 'B7 / B5', 'min_val': 6.0, 'max_val': 0.0, 'breaks': 5, 'color_palette': 'RdYlGn'},
                    {'id': 4, 'name': 'Enhanced Vegetation Index', 'acronym': 'EVI2', 'description': 'In areas of dense canopy where the leaf area index (LAI) is high, the NDVI values can be improved by leveraging information in the blue wavelength. Information in this portion of the spectrum can help correct for soil background signals and atmospheric influences.', 'formula': '(2.5*(B8 - B4) / (B8 + 6*B4 - 7.5*B2 + 1)) * (B3 < 1000)', 'min_val': 0.0, 'max_val': 10.0, 'breaks': 5, 'color_palette': 'Spectral'},
                    {'id': 1, 'name': 'Natural Difference Vegetation Index', 'acronym': 'NDVI', 'description': '', 'formula': '(B8 - B4) / (B8 + B4)', 'min_val': -1.0, 'max_val': 1.0, 'breaks': 0, 'color_palette': 'RdYlGn'},
                    {'id': 37, 'name': 'Normalized Built-up Area Index', 'acronym': 'NBAI', 'description': 'Landsat-7 formula:\r\n\r\nNBAI = (TM7 – TM5/TM2)/ (TM7 + TM5/TM2)\r\n\r\nGeneric Name\t                                Sentinel-2\t        Landsat-7\t   Landsat-8\r\nShort Wave Infra-Red 2 (SWIR2)\t12 (2100–2280)\t7 (2090–2350)\t   7 (2110–2290)\r\nShort Wave Infra-Red 1 (SWIR1)\t11 (1565–1655)\t5 (1550–1750)\t   6 (1570–1650)\r\nGreen\t                                          3 (543–578)\t        2 (520–600)\t   3 (530–590)\r\n\r\nOur conversion:\r\nNBAI = (B12 - B11/B3)/(B12 + B11/B3)\r\n\r\nReference:\r\n\r\nhttps://www.researchgate.net/publication/284816904_Development_of_new_indices_for_extraction_of_built-up_area_and_bare_soil_from_landsat', 'formula': '((B12 - B11/B3)/(B12 + B11/B3)) * (B3 < 1500)', 'min_val': 0.0, 'max_val': 5.0, 'breaks': 9, 'color_palette': 'YlOrRd'},
                    {'id': 34, 'name': 'Normalized Difference Water Index+', 'acronym': 'NDWI+', 'description': 'The NDWI index is most appropriate for water body mapping. The water body has strong absorbability and low radiation in the range from visible to infrared wavelengths. The index uses the green and Near Infra-red bands of remote sensing images based on this phenomenon. \r\n\r\nValues description: Values of water bodies are larger than 0.5. Vegetation has much smaller values, which results in distinguishing vegetation from water bodies easier. Built-up features have positive values between zero and 0.2.', 'formula': '(B3 - B8) / (B3 + B8) * (B3 < 1500)', 'min_val': 0.25, 'max_val': 1.0, 'breaks': 5, 'color_palette': 'Blues'},
                    {'id': 35, 'name': 'Photochemical Reflectance Index', 'acronym': 'PRI', 'description': 'Photochemical Reflectance Index (PRI) provides an important indication of site-specific photosynthetic stress on leaf level in relation to limitations in soil water availability.\r\n\r\nBest bands in theory were adapted by Geodesign Technologies to Sentinel-2 imagery.\r\n\r\n(P531 - p570 ) / p531 + P570', 'formula': '(B2 - B3 ) / (B2 + B3)', 'min_val': -1.0, 'max_val': 1.0, 'breaks': 5, 'color_palette': 'PuOr'},
                    {'id': 3, 'name': 'Positive Clear NDVI', 'acronym': 'NDVI+', 'description': 'Vegetation as measured by positive NDVI scores.', 'formula': '((B8 - B4) / (B8 + B4)) * (B3 < 1500)', 'min_val': 0.25, 'max_val': 0.75, 'breaks': 1, 'color_palette': 'Greens'},
                    {'id': 68, 'name': 'SAVI - Agriculture', 'acronym': 'SAVI - Ag', 'description': 'SAVI - Agriculture', 'formula': '(1.5 * ((B8 - B4)/(B8 + B4 + 0.5)))', 'min_val': 0.5, 'max_val': 1.1, 'breaks': 0, 'color_palette': 'Oranges'},
                    {'id': 69, 'name': 'SAVI - Forest', 'acronym': 'SAVI - Forest', 'description': 'SAVI - Forest', 'formula': '(1.5 * ((B8 - B4)/(B8 + B4 + 0.5)))', 'min_val': 1.1, 'max_val': 1.5, 'breaks': 0, 'color_palette': 'Greens'},
                    {'id': 67, 'name': 'SAVI - Non Vegetated', 'acronym': 'SAVI - NonVeg', 'description': 'savi - non vegetated', 'formula': '(1.5 * ((B8 - B4)/(B8 + B4 + 0.5)))', 'min_val': 0.0, 'max_val': 0.5, 'breaks': 0, 'color_palette': 'Reds'},
                ]
            }

    return MockResponse()


def mock_get_formula_detail(session, url):

    class MockResponse(TesselateMockResponseBase):

        def json(self):
            return {'id': 36, 'name': 'Chlorophyll Index', 'acronym': 'CI', 'description': 'Chlorophyll Index', 'formula': 'B7 / B5', 'min_val': 6.0, 'max_val': 0.0, 'breaks': 5, 'color_palette': 'RdYlGn'}

    return MockResponse()


def mock_create_formula(session, url, json):

    class MockResponse(TesselateMockResponseBase):

        def json(self):
            json.update({'id': 1})
            return json

    return MockResponse()


def mock_update_formula(session, url, json):

    class MockResponse(TesselateMockResponseBase):

        def json(self):
            orig = {'id': 36, 'name': 'Chlorophyll Index', 'acronym': 'CI', 'description': 'Chlorophyll Index', 'formula': 'B7 / B5', 'min_val': 6.0, 'max_val': 0.0, 'breaks': 5, 'color_palette': 'RdYlGn'}
            orig.update(json)
            return orig

    return MockResponse()


def mock_delete_formula(session, url):

    return TesselateMockResponseBase()


class TestTesselateClient(unittest.TestCase):

    def setUp(self):
        os.environ['TESSELO_ACCESS_TOKEN'] = 'tesselate test token env'
        self.ts = Tesselate()

    @mock.patch('tesselate.client.requests.Session.get', mock_get_formula_list)
    def test_get_formula_list(self):
        response = self.ts.formula()
        self.assertEqual(response[0]['acronym'], 'CI')

    @mock.patch('tesselate.client.requests.Session.get', mock_get_formula_detail)
    def test_get_formula_detail(self):
        response = self.ts.formula(id=36)
        self.assertEqual(response['acronym'], 'CI')

    @mock.patch('tesselate.client.requests.Session.post', mock_create_formula)
    def test_create_formula(self):
        response = self.ts.formula(data={'name': 'Chlorophyll Index', 'acronym': 'CI', 'description': 'Chlorophyll Index', 'formula': 'B7 / B5', 'min_val': 6.0, 'max_val': 0.0, 'breaks': 5, 'color_palette': 'RdYlGn'})
        self.assertEqual(response['id'], 1)

    @mock.patch('tesselate.client.requests.Session.patch', mock_update_formula)
    def test_update_formula(self):
        response = self.ts.formula(data={'id': 1, 'name': 'Banana Stand'})
        self.assertEqual(response['name'], 'Banana Stand')

    @mock.patch('tesselate.client.requests.Session.get', mock_get_formula_detail)
    def test_get_formula_detail_non_json(self):
        response = self.ts.formula(id=36, json_response=False)
        self.assertEqual(response['acronym'], 'CI')

    @mock.patch('sys.stdout.write', lambda x: None)
    @mock.patch('tesselate.client.requests.Session.delete', mock_delete_formula)
    @mock.patch('builtins.input', lambda: 'yes')
    def test_delete_formula_yes(self):
        response = self.ts.formula(id=36, delete=True)
        self.assertIsNone(response)

    @mock.patch('sys.stdout.write', lambda x: None)
    @mock.patch('builtins.input', lambda: 'no')
    def test_delete_formula_no(self):
        response = self.ts.formula(id=36, delete=True)
        self.assertIsNone(response)
