import urllib

from tesselate import const


def algebra(client, tilez, tilex, tiley, composite, formula):
    # Construct layers lookup parameter.
    layers = []
    for key, layer in const.LOOKUP.items():
        if key in formula['formula']:
            layers.append('{}={}'.format(key, composite['rasterlayer_lookup'][layer]))
    layers = ','.join(layers)
    # Encode formula.
    formula_encoded = urllib.parse.quote(formula['formula'].replace(' ', ''), safe='()/')
    # Consturct url.
    url = 'algebra/{}/{}/{}.tif?formula={}&layers={}'.format(tilez, tilex, tiley, formula_encoded, layers)
    # Fetch tile.
    return client.get(url, json_response=False)


def rgb(client, tilez, tilex, tiley, composite):
    # Construct url.
    url = 'algebra/{}/{}/{}.png?layers=r={},g={},b={}&scale=0,4e3&alpha&enhance_brightness=1.6&enhance_sharpness=1.2&enhance_color=1.2&enhance_contrast=1.1'.format(
        tilez,
        tilex,
        tiley,
        composite['rasterlayer_lookup']['B04.jp2'],
        composite['rasterlayer_lookup']['B03.jp2'],
        composite['rasterlayer_lookup']['B02.jp2'],
    )
    return client.get(url, json_response=False)
