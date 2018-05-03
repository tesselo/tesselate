import logging

from django.conf import settings
from tesselate.aggregation import aggregate, regional_aggregate
from tesselate.client import Client
from tesselate.export import export
from tesselate.utils import z_scores_grouping

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


class Tesselate(object):

    def __init__(self):
        # For the raster tilesize function.
        try:
            settings.configure()
        except:
            pass

        # instantiate the client.
        self.client = Client()

    def region(self, pk=None, **filters):
        return self.client.dispatch('aggregationlayer', pk=pk, **filters)

    def area(self, pk=None, **filters):
        return self.client.dispatch('aggregationarea', pk=pk, **filters)

    def composite(self, pk=None, **filters):
        return self.client.dispatch('composite', pk=pk, **filters)

    def scene(self, pk=None, **filters):
        return self.client.dispatch('sentineltile', pk=pk, **filters)

    def formula(self, pk=None, **filters):
        return self.client.dispatch('formula', pk=pk, **filters)

    def trainingsample(self, pk=None, **filters):
        return self.client.dispatch('trainingsample', pk=pk, **filters)

    def export(self, region, composite, formula, file_path, tilez=14):
        export(self.client, region, composite, formula, file_path, tilez=14)

    def aggregate(self, area, composite, formula, grouping='continuous'):
        return aggregate(self.client, area, composite, formula, grouping)

    def regional_aggregate(self, valuecounts):
        return regional_aggregate(valuecounts)

    def z_scores_grouping(self, mean, std):
        return z_scores_grouping(mean, std)
