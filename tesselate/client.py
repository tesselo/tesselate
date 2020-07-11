import logging
import os
from urllib.parse import urlencode

import requests

from tesselate.utils import confirm


class Client(object):

    api = 'https://api.tesselo.com/'

    session = None

    def __init__(self):
        # Get token from env if available.
        if 'TESSELO_ACCESS_TOKEN' in os.environ:
            token = os.environ.get('TESSELO_ACCESS_TOKEN')
            self.set_token(token)

    def raise_for_status(self, response):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            logging.error(response.text)
            raise

    def authenticate(self, username, password):
        """
        Authinticate a user by getting a fresh auth token.
        """
        response = requests.post(self.api + 'token-auth/', data={'username': username, 'password': password})

        self.raise_for_status(response)

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
        self.raise_for_status(response)

        if json_response:
            return response.json()
        else:
            return response.content

    def post(self, url, data={}):
        # Add api root if its not part of the url.
        if not url.startswith(self.api):
            url = self.api + url

        # Get response.
        response = self.session.post(url, json=data)

        # Check for errors in response.
        self.raise_for_status(response)

        return response.json()

    def patch(self, url, data):
        # Add api root if its not part of the url.
        if not url.startswith(self.api):
            url = self.api + url

        # Get response.
        response = self.session.patch(url, json=data)

        # Check for errors in response.
        self.raise_for_status(response)

        return response.json()

    def delete(self, url, force=False):
        # Add api root if its not part of the url.
        if not url.startswith(self.api):
            url = self.api + url

        # Ask for user confirmation.
        if not force and not confirm('delete the object at {}'.format(url)):
            return

        # Get response.
        response = self.session.delete(url)

        # Check for errors in response.
        self.raise_for_status(response)

    def dispatch(self, endpoint, **kwargs):
        """
        Dispatch REST requests.
        """
        # Get json response keyword.
        json_response = kwargs.pop('json_response', True)

        # Get data arg if available.
        data = kwargs.pop('data', {})

        # Get id using either id or id keyword.
        if 'id' in data:
            id = data.get('id', None)
        else:
            id = kwargs.pop('id', None)

        # Add id to endpoint if provided.
        if id:
            # Add id to endpoint
            endpoint += '/{}'.format(id)

            # Handle delete case.
            if kwargs.pop('delete', False):
                force = kwargs.pop('force', False)
                return self.delete(endpoint, force=force)

        # Check if this is a persmissions update request.
        user = kwargs.pop('user', None)
        group = kwargs.pop('group', None)
        invitee = None

        if user and group:
            raise ValueError('User and group permissions can not be updated simultaneously.')
        if user:
            invitee = user
            model = 'user'
        if group:
            invitee = group
            model = 'group'

        # Check if this an permissions management call.
        permission = kwargs.pop('permission', None)
        action = kwargs.pop('action', None)

        if permission and not invitee:
            raise ValueError('Specify either user or group for permissions update.')

        if permission and not action:
            raise ValueError('Specify an action for permissions update.')

        if permission and action and invitee:
            if action not in ('invite', 'exclude'):
                raise ValueError('Permission action needs to be either "invite" or "exclude".')
            if permission not in ('view', 'change', 'delete'):
                raise ValueError('Permission needs to be either "view", "change" or "delete."')

            # Construct update url.
            permissions_url = '/{action}/{model}/{permission}/{invitee}'.format(
                action=action,
                model=model,
                permission=permission,
                invitee=invitee,
            )
            endpoint += permissions_url

            # Set json response to false, the invite endpoint returns an empty
            # response.
            json_response = False

        # Convert remaining kwargs to url parameters.
        if kwargs:
            params = urlencode(kwargs, safe='[]{}()=/')
            endpoint += '?{}'.format(params)

        # For requests with data, dispatch post or patch.
        if data:
            if id:
                response = self.patch(endpoint, data)
            else:
                response = self.post(endpoint, data)
        else:
            response = self.get(endpoint, json_response=json_response)

        if json_response:
            if isinstance(response, dict):
                # Determine current page number.
                if response.get('next', None):
                    page = int(response['next'].split('page=')[1].split('&')[0]) - 1
                    # Compute number of pages.
                    page_size = len(response['results'])
                    page_count = int(response['count'] / page_size) + 1
                elif response.get('previous', None):
                    page = response['previous'].split('page=')

                    if len(page) == 2:
                        page = int(page[1].split('&')[0]) + 1
                    else:
                        page = 2

                    if response.get('next', None):
                        # Compute number of pages.
                        page_size = len(response['results'])
                        page_count = int(response['count'] / page_size) + 1
                    else:
                        # This is the last page.
                        page_count = page
                else:
                    page = None
                # In pagination case, print warning.
                if page is not None:
                    logging.warning('Your query is paginated. Retrieved page {page} out of {page_count} ({total} results total).'.format(
                        total=response['count'],
                        page=page,
                        page_count=page_count,
                    ))

            # Reduce response to data list.
            if 'results' in response:
                response = response['results']

        return response
