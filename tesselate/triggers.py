from tesselate.utils import confirm


def train(client, classifier):
    """
    Train a classifier.
    """
    msg = 'train the classifier "{}" with id {}'.format(
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
    if not confirm('predict the Predicted Layer id {}'.format(predictedlayer['id'])):
        return

    return client.post('predictedlayer/{}/predict'.format(predictedlayer['id']))


def build(client, compositebuild):
    """
    Build a composite.
    """
    if not confirm('build the CopositeBuild with id {}'.format(compositebuild['id'])):
        return

    return client.post('compositebuild/{}/build'.format(compositebuild['id']))
