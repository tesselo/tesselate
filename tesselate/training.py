from django.contrib.gis.gdal import DataSource

from tesselate.utils import confirm


def ingest(ts, traininglayer, image, shapefile, class_column, valuemap, reset):
    """
    Upload trainingsamples from a shapefile.

    The class_column is the shapefile attribute that contains the class of the
    training patch. The valuemap is a dict with class names as keys and class
    values as integers.

    The image is either a sentineltile or a composite.
    """
    # Delete current training samples.
    if reset and confirm('delete all {} exsiting training sample in this layer.'.format(len(traininglayer['trainingsamples']))):
        for sample_id in traininglayer['trainingsamples']:
            ts.trainingsample(pk=sample_id, delete=True, force=True)
        traininglayer['trainingsamples'] = []

    # Decide if layer input is a scene or a composite.
    if 'interval' in image:
        image_key = 'composite'
    else:
        image_key = 'sentineltile'
    # Open data source.
    ds = DataSource(shapefile)
    # Get layer from data source.
    lyr = ds[0]
    # Create empty training data list.
    trainings = []
    # Get training data from layer.
    for feat in lyr:
        category = feat['class'].as_string()

        if category in valuemap:
            # If the column value is a class name, retrieve the corresponding
            # pixel value.
            category_value = valuemap[category]
        else:
            # If it is an integer, get the class name from the valuemap.
            category_value = int(category)
            category = list(valuemap.keys())[list(valuemap.values()).index(category_value)]

        trainings.append({
            'traininglayer': traininglayer['id'],
            'category': category,
            'value': category_value,
            'geom': feat.geom.ewkt,
            image_key: image['id'],
        })

    # Ask for confirmation before posting the data.
    if not confirm('create {} new training samples for traininglayer {}.'.format(len(trainings), traininglayer['id'])):
        return

    # Post training data.
    for training in trainings:
        response = ts.trainingsample(data=training)
        # Add new training sample to local traininglayer object to keep it in
        # sync with the database.
        traininglayer['trainingsamples'].append(response['id'])

    return traininglayer
