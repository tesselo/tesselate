import sys

from tesselate import const


def confirm(message):
    # Ask for user confirmation.
    sys.stdout.write('Type "yes" to confirm you want to {} -- '.format(message))
    if input().lower() != 'yes':
        sys.stdout.write('The answer was not "yes", aborted operation')
        return False
    else:
        return True


def layers_dict(composite, formula):
    """
    Construct layers dictionary for algebra and aggregation calls.
    """
    layers = {}
    for key, layer in const.LOOKUP.items():
        if key in formula['formula']:
            layers[key] = composite['rasterlayer_lookup'][layer]
    return layers


def layers_query_arg(composite, formula):
    """
    Construct layers query argument for algebra tile requests.
    """
    layers = layers_dict(composite, formula)
    return ','.join(['{}={}'.format(key, val) for key, val in layers.items()])


def z_scores_grouping(mean, std):
    """
    Get a grouping parameter with z-scores breaks from the input mean and std.
    """
    # Compute breaks.
    very_low = mean - 2 * std
    low = mean - std
    high = mean + std
    very_high = mean + 2 * std
    # Create grouping list.
    return [
        {"color": "#d7191c", "name": "Very low", "expression": "x<{0}".format(very_low)},
        {"color": "#fdae61", "name": "Low", "expression": "(x>={0}) & (x<={1})".format(very_low, low)},
        {"color": "#ffffbf", "name": "Average", "expression": "(x>{0}) & (x<{1})".format(low, high)},
        {"color": "#a6d96a", "name": "High", "expression": "(x>={0}) & (x<={1})".format(high, very_high)},
        {"color": "#1a9641", "name": "Very High", "expression": "x>{0}".format(very_high)},
    ]


def populate_aggregation_areas(client, region):
    """
    Request aggregation area objects from api and store them in the region dict.
    """
    for index, id in enumerate(region['aggregationareas']):
        # Only get the data if the area is indeed a primary key integer.
        if isinstance(id, int):
            region['aggregationareas'][index] = client.dispatch('aggregationarea', id=id)
