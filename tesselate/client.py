import logging
import os
from urllib.parse import urlencode

import requests


class Client(object):

    api = 'https://tesselo.com/api/'

    session = None

    def __init__(self):
        # Get token from env if available.
        if 'TESSELO_ACCESS_TOKEN' in os.environ:
            token = os.environ.get('TESSELO_ACCESS_TOKEN')
            self.set_token(token)

    def authenticate(self, username, password):
        """
        Authinticate a user by getting a fresh auth token.
        """
        response = requests.post(self.api + 'token-auth/', data={'username': username, 'password': password})

        response.raise_for_status()

        response = response.json()

        self._username = username
        self._token_expires = response['expires']

        logging.info('Authenticated {} successfully. Token expires on {}.'.format(self._username, self._token_expires))

        self.set_token(response['token'])

    def set_token(self, token):
        """
        Initiate requests session with a standard token-based authorization header.
        """
        self.token = token

        auth_header = {'Authorization': 'Token {}'.format(token)}

        self.session = requests.Session()
        self.session.headers.update(auth_header)

    def get(self, url, json_response=True):
        """
        Make a get request to api. Assumes json response. The input url can be passed
        without api root.
        """
        logging.debug('GET Request {}'.format(url))

        # Add api root if its not part of the url.
        if not url.startswith(self.api):
            url = self.api + url

        # Get response.
        response = self.session.get(url)

        # Check for errors in response.
        response.raise_for_status()

        if json_response:
            return response.json()
        else:
            return response.content

    def get_rest(self, endpoint, pk=None, **filters):
        if pk:
            endpoint += '/{}'.format(pk)

        if filters:
            params = urlencode(filters, safe='[]{}()=/')
            endpoint += '?{}'.format(params)

        response = self.get(endpoint)

        if response.get('next', None):
            logging.warning('Your query has {} results, only the first {} retrieved.'.format(response['count'], len(response['results'])))

        # Reduce response to data list.
        if 'results' in response:
            response = response['results']

        return response

    def post(self, url, data, json_response=True):
        """
        Make a get request to api. Assumes json response. The input url can be passed
        without api root.
        """
        logging.debug('POST Request {}, {}'.format(url, data))

        # Add api root if its not part of the url.
        if not url.startswith(self.api):
            url = self.api + url

        # Get response.
        response = self.session.post(url, json=data)

        # Check for errors in response.
        response.raise_for_status()

        if json_response:
            return response.json()
        else:
            return response.content
