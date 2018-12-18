import copy
import json
import logging

from tesselate.utils import layers_dict


def aggregate(client, area, composite, formula, grouping='continuous', zoom=None, synchronous=True):
    """
    Request aggregation data.
    """
    # Get layer names for request.
    layer_names = layers_dict(composite, formula)
    # Grouping parameter needs to be a string.
    if isinstance(grouping, (list, tuple)):
        grouping = json.dumps(grouping)
    # Construct query parameters.
    post_params = {
        'aggregationarea': area['id'],
        'layer_names': layer_names,
        'formula': formula['formula'].replace(' ', ''),
        'grouping': grouping,
        'acres': 'True',
    }
    # Add manual zoom level override if provided.
    if zoom is not None:
        post_params['zoom'] = zoom
    # Create GET version of query parameters. The layer names dict needs to be
    # contained in the url query parameters.
    get_params = copy.deepcopy(post_params)
    get_params['layer_names'] = json.dumps(layer_names)
    # Try to get result from cache.
    result = client.dispatch('valuecountresult', **get_params)
    if len(result):
        return result[0]
    else:
        # If valuecount has not been precomputed, do it now synchronously.
        logging.info('Value count not precomputed, requesting {} calculation.'.format('synchronous' if synchronous else 'asynchronous'))
        return client.post('valuecountresult{}'.format('?synchronous' if synchronous else ''), data=post_params)


def regional_aggregate(valuecounts):
    """
    Use the cumsum and sq_cumsum from valuecounts to compute regional stats.
    """
    # Compute sum of sums.
    stats_t0 = sum([dat['pcount'] for dat in valuecounts])
    stats_t1 = sum([dat['psum'] for dat in valuecounts])
    stats_t2 = sum([dat['psumsq'] for dat in valuecounts])
    # Get total min and max values.
    stats_min = min([dat['min'] for dat in valuecounts])
    stats_max = min([dat['max'] for dat in valuecounts])
    # Compute regional mean and std.
    if stats_t0 == 0:
        # If totals sum is zero, no data was available to comput statistics
        mean = None
        std = None
    else:
        # Compute mean and std from totals sums.
        mean = stats_t1 / stats_t0
        std = (stats_t0 * stats_t2 - stats_t1 * stats_t1) ** 0.5 / stats_t0

    return {
        'min': stats_min,
        'max': stats_max,
        'std': std,
        'mean': mean,
    }
