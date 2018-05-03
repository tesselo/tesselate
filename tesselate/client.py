import logging
import os
import sys
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

    def post(self, url, data):
        # Add api root if its not part of the url.
        if not url.startswith(self.api):
            url = self.api + url

        # Get response.
        response = self.session.post(url, json=data)

        # Check for errors in response.
        response.raise_for_status()

        return response.json()

    def patch(self, url, data):
        # Add api root if its not part of the url.
        if not url.startswith(self.api):
            url = self.api + url

        # Get response.
        response = self.session.patch(url, json=data)

        # Check for errors in response.
        response.raise_for_status()

        return response.json()

    def delete(self, url):
        # Add api root if its not part of the url.
        if not url.startswith(self.api):
            url = self.api + url

        # Ask for user confirmation.
        sys.stdout.write('Type "yes" to confirm you want to delete the object at {} -- '.format(url))
        if input().lower() != 'yes':
            sys.stdout.write('The answer was not "yes", aborted operation')
            return

        # Get response.
        response = self.session.delete(url)

        # Check for errors in response.
        response.raise_for_status()

    def dispatch(self, endpoint, **kwargs):
        """
        Dispatch REST requests.
        """
        # Get data arg if available.
        data = kwargs.pop('data', {})

        # Get pk using either id or pk keyword.
        if 'id' in data:
            pk = data.get('id', None)
        else:
            pk = kwargs.pop('pk', None)

        # Add pk to endpoint if provided.
        if pk:
            # Add pk to endpoint
            endpoint += '/{}'.format(pk)

            # Handle delete case.
            if 'delete' in kwargs:
                return self.delete(endpoint)

        # Get json response keyword.
        json_response = kwargs.pop('json_response', True)

        # Convert remaining kwargs to url parameters.
        if kwargs:
            params = urlencode(kwargs, safe='[]{}()=/')
            endpoint += '?{}'.format(params)

        # For requests with data, dispatch post or patch.
        if data:
            if pk:
                response = self.patch(endpoint, data)
            else:
                response = self.post(endpoint, data)
        else:
            response = self.get(endpoint, json_response=json_response)

        if json_response:
            if response.get('next', None):
                logging.warning('Your query has {} results, only the first {} retrieved.'.format(response['count'], len(response['results'])))

            # Reduce response to data list.
            if 'results' in response:
                response = response['results']

        return response
