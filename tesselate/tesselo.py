import logging

from django.conf import settings
from tesselate.aggregation import aggregate as agg_funk
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


def export(region, composite, formula, file_path, tilez=14):
    exp_funk(client, region, composite, formula, file_path, tilez=14)


def aggregate(area, composite, formula, grouping='continuous'):
    return agg_funk(client, area, composite, formula, grouping)
