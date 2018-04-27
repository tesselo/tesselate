import logging

from django.conf import settings
from tesselate.client import Client
from tesselate.export import export as exp_funk

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

# Instanciate the client.
client = Client()

# For the raster tilesize function.
try:
    settings.configure()
except:
    pass

client = Client()

def region(pk=None, **filters):
    return client.get_rest('aggregationlayer', pk=pk, **filters)


def area(pk=None, **filters):
    return client.get_rest('aggregationarea', pk=pk, **filters)


def composite(pk=None, **filters):
    return client.get_rest('composite', pk=pk, **filters)


def formula(pk=None, **filters):
    return client.get_rest('formula', pk=pk, **filters)


def export(area, composite, formula, base_path='/tmp', tilez=14):
    exp_funk(client, area, composite, formula, base_path, tilez=14)
