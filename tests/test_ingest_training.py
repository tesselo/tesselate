import os
import unittest

import mock
from tests.utils import TesselateMockResponseBase

from tesselate import Tesselate


def mock_create_trainingsample(session, url, json):

    class MockResponse(TesselateMockResponseBase):

        def json(self):
            json.update({'id': 1})
            return json

    return MockResponse()


def mock_update_classifier(session, url, json):

    class MockResponse(TesselateMockResponseBase):

        def json(self):
            return json

    return MockResponse()


@mock.patch('tesselate.client.requests.Session.post', mock_create_trainingsample)
@mock.patch('tesselate.client.requests.Session.patch', mock_update_classifier)
@mock.patch('builtins.input', lambda: 'yes')
@mock.patch('sys.stdout.write', lambda x: None)
class TestTesselateTriggers(unittest.TestCase):

    def setUp(self):
        self.ts = Tesselate()
        self.shapefile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/training.shp')

    def test_ingestion(self):
        # classifier, scene, shapefile, class_column, valuemap
        classifier = {'id': 1}
        scene = {'id': 2}
        class_column = 'class'
        valuemap = {
            'burn': 1,
            'soil': 2,
            'other': 3,
            'bamboo': 4,
        }

        response = self.ts.ingest(classifier, scene, self.shapefile, class_column, valuemap)
        self.assertEqual(len(response['trainingsamples']), 20)
