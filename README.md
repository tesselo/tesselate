# Tesselate - Tesselo's Python SDK

Copyright &copy; 2018 Tesselo, all rights reserved.

## Docs

### Instantiate Tesselate and authenticate

Tesselate will authenticate using the auth token from the environment if the
`TESSELO_ACCESS_TOKEN` environment variable is set when instantiating
a new instance.

Alternatively, set the token manually or authenticate using your `username` and
`password` credentials as follows.

```python
from tesselate import Tesselate

# With TESSELO_ACCESS_TOKEN in the environment Tesselate is ready to go without
# authentication.
ts = Tesselate()

# Set the token manually.
ts.client.set_token('mysecrettoken')

# Authenticate with your credentials (will set token internally).
ts.client.authenticate('lucille_bluth', 'shawnparmegian')
```

### Retrieve data

Get a list of composites or scenes as JSON dictionaries as follows

```python
# List monthly composites between two dates.
ts.composite(min_date_0='2017-04-01', min_date_1='2018-03-31', interval='Monthly')
# List scenes for a location between two dates.
ts.scene(coords='3991669.5,1278364.1', collected_after='2017-11-30', collected_before='2018-12-02')
```

### Write data

To create new objects, call the endpoint with a dictionary containging the data
for the new object in the `data` keyword. For example, create a new formula as
follows

```python
formula_data = {
     'name': 'Natural Difference Vegetation Index',
     'acronym': 'NDVI',
     'description': 'Index for vegetation density.',
     'formula': '(B8 - B4) / (B8 + B4)',
     'min_val': -1.0,
     'max_val': 1.0,
     'breaks': 0,
     'color_palette': 'RdYlGn',
}
# This will create a new object and return it (including the new pk).
ts.formula(data=formula_data)
```

To update an existing object, pass the primary key as `id` key in the
dictionary. Tesselate will detect the primary key and update the corresponding
object. For example, update the description of a formula with primary key 23 as
follows

```python
formula_update = {
    'id': 23,
    'description': 'This index is a proxy for vegetation density.',
}
# This will update the description of the formula with pk 23.
ts.formula(data=formula_update)
```

### Delete data

To remove entries entirely, pass the `delete` and `pk` keywords to the endpoint.
The following will delete the formula with the primary key 23

```python
ts.formula(pk=23, delete=True)
```

### Retrieve users and groups permissions

A list of user and group permissions can be retrieved using

```python
# List user permissions on a formula.
ts.formula(pk=23, users=True)
# List group permissions on a formula.
ts.formula(pk=23, groups=True)
```

### Update permissions

Permissions can be managed by adding three keywords together: `action`,
`invite`, and `invitee`.

* The `action` keyword is either `invite` or `exclude` and controls what action
  to take.
* The `permission` keyword either `view`, `change`, or `delete` and specifies
  what permission to set.
* The `invitee` keyword is a user or group dictionary and is the invitee of
  the permission to change.

The following examples show a few use cases to manage permissions on a formula.

```python
# Get one user an one group.
lucille = ts.user(search='lucille')[0]
bluths = ts.group(search='bluth family')[0]

# Get a formula.
ndvi = ts.formula(search='NDVI')[0]

# Invite lucille to change the formula.
ts.formula(pk=ndvi['id'], action='invite', permission='change', invitee=lucille)

# Invite all bluths to view the formula.
ts.formula(pk=ndvi['id'], action='invite', permission='view', invitee=bluths)

# Make sure the bluths can not delete the formula.
ts.formula(pk=form['id'], action='exclude', permission='delete', invitee=bluths)

# List the users and groups with permissions on the formula (see previous section).
ts.formula(pk=form['id'], users=True)
ts.formula(pk=form['id'], groups=True)
```

### Schedule tasks

Several long running tasks can be scheduled with function calls. The available
triggers are listed below. All trigger functions prompt the user for
confirmation.

#### Build a Composite

```python
# Get a composite.
composite = ts.composite(min_date_0='2017-04-01', min_date_1='2018-03-31', interval='Monthly')[0]
# Trigger the build for the composite.
ts.build(composite)
```

#### Train a Classifier

```python
# Get a classifier.
classifier = ts.classifier(search='Landcover')[0]
# Trigger training of the classifier.
ts.train(classifier)
```

#### Predict a layer

```python
# Get a predicted layer (contains info about area and classifier to use).
predictedlayer = ts.predictedlayer()[0]
# Trigger prediction of the layer.
ts.predict(predictedlayer)
```

## Ingest training data

Training data polygons can be ingested using an utility function. The training
data needs to be provided as a polygon shapefile layer. The function has the
following required arguments:

- *classifier*: The training data will be attached to a classifier that can use
  the data for training.
- *image*: The training data is assumed to be "drawn" over a scene or a composite.
  So either a scene or a composite is required.
- *shapefile*: An absoulte path to a shapefile.
- *class_column*: The name of the column in the attribute table that contains
  the training class. Either an integer or a string column.
- *valuemap*: A dictionary with class names as keys and class
  values as integers. If integers are found in the class_column, the dict will
  be used to extract class names and vice versa.

The function can be called as follows. A user confirmation will be requested
before writing any data.

```python
# Get a classifier.
classifier = ts.classifier(search='Landcover')[0]
# Get the composite over which the training was "drawn". This could also be a
# scene, both are accepted.
composite = ts.composite(min_date_0='2017-04-01', min_date_1='2018-03-31')[0]
# Set path, column name and valuemap.
shp_path = '/path/to/shapefile.shp'
class_column = 'high_or_low'
valuemap = {'high': 1, 'low': 2}
# Upload training samples.
response = self.ts.ingest(classifier, scene, shp_path, 'name', valuemap)
```

## Logging

Tesselate uses the default python logger. Logging can be set to either `DEBUG`,
`INFO`, `WARNING`, or `ERROR`. The first is the most verbose, and the last the
least verbose setting. Defaults to `INFO`. The following example sets the log
level to `DEBUG`.

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## Testing

To run the test, install mock with `pip install mock` and run tests with

    python -m unittest discover

To see test coverage, install coverage with `pip install coverage` and get
coverage with

    coverage run -m unittest discover
    coverage report -m --include=tesselate/*
