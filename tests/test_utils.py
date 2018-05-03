import unittest

from tesselate.utils import layers_dict, layers_query_arg, z_scores_grouping


class TestTesselateUtils(unittest.TestCase):

    def setUp(self):
        self.composite = {
            'rasterlayer_lookup': {
                'B05.jp2': 1,
                'B07.jp2': 2,
            }
        }
        self.formula = {
            'formula': 'B7 / B5',
        }


    def test_layers_dict(self):
        expected = {
            'B5': 1,
            'B7': 2,
        }

        self.assertEqual(layers_dict(self.composite, self.formula), expected)

    def test_layers_query_arg(self):
        self.assertIn(
            layers_query_arg(self.composite, self.formula),
            ('B7=2,B5=1', 'B5=1,B7=2'),
        )

    def test_z_scores_grouping(self):
        self.assertEqual(
            z_scores_grouping(2.3, 1.3),
            [
                {'expression': 'x<-0.30000000000000027', 'name': 'Very low', 'color': '#d7191c'},
                {'expression': '(x>=-0.30000000000000027) & (x<=0.9999999999999998)', 'name': 'Low', 'color': '#fdae61'},
                {'expression': '(x>0.9999999999999998) & (x<3.5999999999999996)', 'name': 'Average', 'color': '#ffffbf'},
                {'expression': '(x>=3.5999999999999996) & (x<=4.9)', 'name': 'High', 'color': '#a6d96a'},
                {'expression': 'x>4.9', 'name': 'Very High', 'color': '#1a9641'}
            ],
        )
