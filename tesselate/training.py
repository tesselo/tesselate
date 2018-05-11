from django.contrib.gis.gdal import DataSource
from tesselate.utils import confirm


def ingest(ts, classifier, scene, shapefile, class_column, valuemap):
    """
    Upload trainingsamples from a shapefile.

    The class_column is the shapefile attribute that contains the class of the
    training patch. The valuemap is a dict with class names as keys and class
    values as integers.
    """
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
            'category': category,
            'value': category_value,
            'geom': feat.geom.ewkt,
            'sentineltile': scene['id'],
        })

    # Ask for confirmation before posting the data.
    if not confirm('create {} new training samples for classifier {}.'.format(len(trainings), classifier['id'])):
        return

    # Post training data.
    training_ids = []
    for training in trainings:
        response = ts.trainingsample(data=training)
        training_ids.append(response['id'])

    # Bind the training data to the classifier.
    classifier.update({'trainingsamples': training_ids})
    ts.classifier(data=classifier)

    return classifier
