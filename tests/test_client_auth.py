import os
import unittest

import mock

from tesselate import Tesselate


def mock_authenticate(url, data):

    class MockAuthResponse(object):

        def raise_for_status(self):
            pass

        def json(self):
            return {'token': 'tesselate test token api', 'expires': '1953'}

    return MockAuthResponse()


class TestTesselateClientAuth(unittest.TestCase):

    def setUp(self):
        os.environ['TESSELO_ACCESS_TOKEN'] = 'tesselate test token env'
        self.ts = Tesselate()

    def test_token_from_env(self):
        self.assertEqual(self.ts.client.token, 'tesselate test token env')

    def test_set_token(self):
        self.ts.client.set_token('tesselate test token set')
        self.assertEqual(self.ts.client.token, 'tesselate test token set')
        self.assertEqual(self.ts.client.session.headers['Authorization'], 'Token tesselate test token set')

    @mock.patch('tesselate.client.requests.post', mock_authenticate)
    def test_authenticate(self):
        self.ts.client.authenticate('lucille', 'shawnparmegian')
        self.assertEqual(self.ts.client.token, 'tesselate test token api')
        self.assertEqual(self.ts.client._username, 'lucille')
        self.assertEqual(self.ts.client._token_expires, '1953')
