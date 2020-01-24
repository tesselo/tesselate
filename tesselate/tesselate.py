import logging

from django.conf import settings

from tesselate.aggregation import aggregate, regional_aggregate
from tesselate.client import Client
from tesselate.export import export
from tesselate.training import ingest
from tesselate.triggers import build, predict, train
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

    def user(self, id=None, **filters):
        return self.client.dispatch('user', id=id, **filters)

    def group(self, id=None, **filters):
        return self.client.dispatch('group', id=id, **filters)

    def region(self, id=None, **filters):
        return self.client.dispatch('aggregationlayer', id=id, **filters)

    def area(self, id=None, **filters):
        return self.client.dispatch('aggregationarea', id=id, **filters)

    def composite(self, id=None, **filters):
        return self.client.dispatch('composite', id=id, **filters)

    def compositebuild(self, id=None, **filters):
        return self.client.dispatch('compositebuild', id=id, **filters)

    def scene(self, id=None, **filters):
        return self.client.dispatch('sentineltile', id=id, **filters)

    def formula(self, id=None, **filters):
        return self.client.dispatch('formula', id=id, **filters)

    def trainingsample(self, id=None, **filters):
        return self.client.dispatch('trainingsample', id=id, **filters)

    def traininglayer(self, id=None, **filters):
        return self.client.dispatch('traininglayer', id=id, **filters)

    def classifier(self, id=None, **filters):
        return self.client.dispatch('classifier', id=id, **filters)

    def predictedlayer(self, id=None, **filters):
        return self.client.dispatch('predictedlayer', id=id, **filters)

    def wmtslayer(self, id=None, **filters):
        return self.client.dispatch('wmtslayer', id=id, **filters)

    def export(self, region, composite, formula, file_path, zoom=14, clip_to_geom=False, all_touched=False):
        return export(self.client, region, composite, formula, file_path, zoom=zoom, clip_to_geom=clip_to_geom, all_touched=all_touched)

    def aggregate(self, area, composite, formula, grouping='continuous', zoom=None, synchronous=True):
        return aggregate(self.client, area, composite, formula, grouping, zoom, synchronous)

    def build(self, compositebuild):
        return build(self.client, compositebuild)

    def train(self, classifier):
        return train(self.client, classifier)

    def predict(self, predictedlayer):
        return predict(self.client, predictedlayer)

    def regional_aggregate(self, valuecounts):
        return regional_aggregate(valuecounts)

    def z_scores_grouping(self, mean, std):
        return z_scores_grouping(mean, std)

    def ingest(self, classifier, scene, shapefile, class_column, valuemap, date_column=None, reset=False):
        return ingest(self, classifier, scene, shapefile, class_column, valuemap, date_column, reset)
