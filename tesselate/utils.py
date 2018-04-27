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
