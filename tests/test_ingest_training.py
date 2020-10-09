import os
import unittest

import mock

from tesselate import Tesselate
from tests.utils import TesselateMockResponseBase


def mock_create_trainingsample(session, url, json):

    class MockResponse(TesselateMockResponseBase):

        def json(self):
            json.update({'id': 1})
            return json

    return MockResponse()


def mock_delete(session, url):

    return TesselateMockResponseBase()


@mock.patch('tesselate.client.requests.Session.post', mock_create_trainingsample)
@mock.patch('tesselate.client.requests.Session.delete', mock_delete)
@mock.patch('builtins.input', lambda: 'yes')
@mock.patch('sys.stdout.write', lambda x: None)
class TestTesselateTriggers(unittest.TestCase):

    def setUp(self):
        self.ts = Tesselate()

    def test_ingestion_discrete(self):
        shapefile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/training.shp')

        # classifier, scene, shapefile, class_column, valuemap
        traininglayer = {'id': 1, 'name': 'Test training layer', 'trainingsamples': [1, 2, 3], 'continuous': False}
        scene = {'id': 2}
        class_column = 'class'
        valuemap = {
            'burn': 1,
            'soil': 2,
            'other': 3,
            'bamboo': 4,
        }

        response = self.ts.ingest(traininglayer, scene, shapefile, class_column, valuemap, reset=False)
        self.assertEqual(len(response['trainingsamples']), 23)

        response = self.ts.ingest(traininglayer, scene, shapefile, class_column, valuemap, reset=True)
        self.assertEqual(len(response['trainingsamples']), 20)

        # The interval key identifies this object as composite.
        composite = {'id': 3, 'interval': 'Monthly'}
        response = self.ts.ingest(traininglayer, composite, shapefile, class_column, valuemap, reset=True)
        self.assertEqual(len(response['trainingsamples']), 20)

    def test_ingestion_continuous(self):
        shapefile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/training_continuous.shp')

        # classifier, scene, shapefile, class_column, valuemap
        traininglayer = {'id': 1, 'name': 'Test training layer', 'trainingsamples': [1, 2, 3], 'continuous': True}
        scene = {'id': 2}
        class_column = 'class'
        valuemap = None

        response = self.ts.ingest(traininglayer, scene, shapefile, class_column, valuemap, reset=False)
        self.assertEqual(len(response['trainingsamples']), 23)

        response = self.ts.ingest(traininglayer, scene, shapefile, class_column, valuemap, reset=True)
        self.assertEqual(len(response['trainingsamples']), 20)

        # The interval key identifies this object as composite.
        composite = {'id': 3, 'interval': 'Monthly'}
        response = self.ts.ingest(traininglayer, composite, shapefile, class_column, valuemap, reset=True)
        self.assertEqual(len(response['trainingsamples']), 20)

    def test_ingestion_discrete_with_date(self):
        shapefile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/training.shp')

        # classifier, scene, shapefile, class_column, valuemap
        traininglayer = {'id': 1, 'name': 'Test training layer', 'trainingsamples': [1, 2, 3], 'continuous': False}
        scene = {'id': 2}
        class_column = 'class'
        valuemap = {
            'burn': 1,
            'soil': 2,
            'other': 3,
            'bamboo': 4,
        }
        date_column = 'date'
        date_string_column = 'date_strin'

        response = self.ts.ingest(traininglayer, scene, shapefile, class_column, valuemap, date_column, reset=True)
        self.assertEqual(len(response['trainingsamples']), 20)

        response = self.ts.ingest(traininglayer, scene, shapefile, class_column, valuemap, date_string_column, reset=True)
        self.assertEqual(len(response['trainingsamples']), 20)

    def test_ingestion_wrong_column_names(self):
        shapefile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/training_continuous.shp')

        # classifier, scene, shapefile, class_column, valuemap
        traininglayer = {'id': 1, 'name': 'Test training layer', 'trainingsamples': [1, 2, 3], 'continuous': True}
        scene = {'id': 2}
        class_column = 'does not exist'
        valuemap = None
        with self.assertRaises(ValueError):
            self.ts.ingest(traininglayer, scene, shapefile, class_column, valuemap, reset=False)

        class_column = 'class'
        date_column = 'does not exist'

        with self.assertRaises(ValueError):
            self.ts.ingest(traininglayer, scene, shapefile, class_column, valuemap, date_column, reset=False)
