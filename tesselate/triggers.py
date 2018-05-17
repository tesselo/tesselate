from tesselate.utils import confirm


def train(client, classifier):
    """
    Train a classifier.
    """
    msg = 'train the classifier "{}" with pk {}'.format(
        classifier['name'],
        classifier['id'],
    )
    if not confirm(msg):
        return

    return client.post('classifier/{}/train'.format(classifier['id']))


def predict(client, predictedlayer):
    """
    Predict a layer.
    """
    if not confirm('predict the Predicted Layer pk {}'.format(predictedlayer['id'])):
        return

    return client.post('predictedlayer/{}/predict'.format(predictedlayer['id']))


def build(client, compositebuild):
    """
    Build a composite.
    """
    if not confirm('build the CopositeBuild with pk {}'.format(compositebuild['id'])):
        return

    return client.post('compositebuild/{}/build'.format(compositebuild['id']))
