from tesselate import const


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
