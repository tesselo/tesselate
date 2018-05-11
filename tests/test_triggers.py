import os
import unittest

import mock
from tests.utils import TesselateMockResponseBase

from tesselate import Tesselate


def mock_trigger(session, url, json):

    class MockResponse(TesselateMockResponseBase):

        def json(self):
            return {}

    return MockResponse()


@mock.patch('tesselate.client.requests.Session.post', mock_trigger)
@mock.patch('builtins.input', lambda: 'yes')
@mock.patch('sys.stdout.write', lambda x: None)
class TestTesselateTriggers(unittest.TestCase):

    def setUp(self):
        os.environ['TESSELO_ACCESS_TOKEN'] = 'tesselate test token env'
        self.ts = Tesselate()

    def test_build_trigger(self):
        response = self.ts.build({'id': 1})
        self.assertEqual(response, {})

    def test_train_trigger(self):
        response = self.ts.train({'id': 1, 'name': 'Test Classifier'})
        self.assertEqual(response, {})

    def test_predict_trigger(self):
        response = self.ts.predict({'id': 1})
        self.assertEqual(response, {})
