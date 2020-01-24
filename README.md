# Tesselate - Tesselo's Python SDK

Copyright &copy; 2018 Tesselo, all rights reserved.

Tesselate is a wrapper for human friendly interaction with Tesselo's API.

The endpoints are represented by functions that all have similar base
functionality. Data can be read, written and updated in a standardized way.

Several long running tasks can be scheduled with function calls. The available
triggers are listed below. All trigger functions prompt the user for
confirmation.

Layers can be aggregated through the api or exported to local files for further
analysis.

## General usage of api endpoints

This section describes the current general functionality of the api wrapper.
Each api endpoint is represented by one function.

Generally, the endpoint functions simply pass on the input keyword arguments as
query arguments. To consult what query arguments are allowed, visit the
browseable api and look at the filter section.

A few exceptions to the general rule are:

- `id` This keyword is interpreted as the ID or primary key of the objects. It
  should be used to get individual objects and to create or update them.
- `data` This keyword is a dictionary with data for the endpoint. If a `id`
  argument is provided or if the `data` dictionary contains an `id` key, the
  data is used to update the corresponding object. Otherwise a new one is
  created.
- `search` Some endpoints allow filtering by loose text search with this keyword.
- `permission` This will trigger permissions changes. See section below for
  details.

### List of supported endpoints

  | Function        | Endpoint | Description |
  | --------------- | -------- | ----------- |
  | group | [/group](https://api.tesselo.com/group) | Lists of groups, read-only |
  | user | [/user](https://api.tesselo.com/user) | List of users, read-only |
  | region | [/aggregationlayer](https://api.tesselo.com/aggregationlayer) | Aggregationlayers serve as regions |
  | area | [/aggregationarea](https://api.tesselo.com/aggregationarea) | Individual aggregation areas |
  | composite | [/composite](https://api.tesselo.com/composite)| Composite layers |
  | compositebuild | [/compositebuild](https://api.tesselo.com/compositebuild)| Composite build objects to track builds |
  | scene | [/sentineltile](https://api.tesselo.com/sentineltile)| Individual sentinel scenes |
  | formula | [/formula](https://api.tesselo.com/formula)| Formulas for algebra rendering and aggregation |
  | trainingsample | [/trainingsample](https://api.tesselo.com/trainingsample)| A single training sample polygon |
  | traininglayer | [/traininglayer](https://api.tesselo.com/traininglayer)| A group of training sample polygons |
  | classifier | [/classifier](https://api.tesselo.com/classifier)| Classifier to train against trainingsamples |
  | predictedlayer | [/predictedlayer](https://api.tesselo.com/predictedlayer)| A layer to predict on with classifier |
  | wmtslayer | [/wmtslayer](https://api.tesselo.com/wmtslayer)| Layers that are added to the WMTS endpoint |

### List of addtional functions

The following is a list of action endpoints, in additon to the data model api
endpoints. These functions are described in more detail below.

| Function | Purpose |
| -------- | ------- |
| export | Export algebra expressions or RGB to local files |
| aggregate | Call aggregation endpoint |
| build | Build a composite |
| train | Train a classifier |
| predict | Predict over a scene or composite using a classifier |
| regional_aggregate | Compute regional aggregates |
| z_scores_grouping | Helper to create z-scores breaks valuecount dictionary |
| ingest | Ingest a shapefile as training data |

## Instantiate Tesselate and authenticate

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

## Retrieve data

Get a list of composites or scenes as JSON dictionaries as follows

```python
# List monthly composites between two dates.
ts.composite(min_date_after='2017-03-01', min_date_before='2018-03-31', interval='Monthly')
# List scenes for a location between two dates.
ts.scene(coords='3991669.5,1278364.1', collected_after='2017-11-30', collected_before='2018-12-02')
```

## Write data

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
# This will create a new object and return it (including the new id).
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
# This will update the description of the formula with id 23.
ts.formula(data=formula_update)
```

## Delete data

To remove entries entirely, pass the `delete` and `id` keywords to the endpoint.
The following will delete the formula with the primary key 23

```python
ts.formula(id=23, delete=True)
```

The delete method will ask for user confirmation by default. To force deletion
without user input (for use in scripts for instance), pass `force=True` to the
function. The following example will delete the object with primary key 23
without asking for user confirmation

```python
ts.formula(id=23, delete=True, force=True)
```

## Retrieve users and groups permissions

A list of user and group permissions can be retrieved using

```python
# List user permissions on a formula.
ts.formula(id=23, users=True)
# List group permissions on a formula.
ts.formula(id=23, groups=True)
```

## Update permissions

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
ts.formula(id=ndvi['id'], action='invite', permission='change', invitee=lucille)

# Invite all bluths to view the formula.
ts.formula(id=ndvi['id'], action='invite', permission='view', invitee=bluths)

# Make sure the bluths can not delete the formula.
ts.formula(id=form['id'], action='exclude', permission='delete', invitee=bluths)

# List the users and groups with permissions on the formula (see previous section).
ts.formula(id=form['id'], users=True)
ts.formula(id=form['id'], groups=True)
```

## Build Composites

To build a compoiste, create a compositebuild object and trigger the build by
passing the compositebuild object to the build function.

```python
# Create a new composite build object.
composite = ts.composite(min_date_after='2017-03-01', min_date_before='2018-03-31', interval='Monthly')[0]

region = ts.region(search='Orange County')

lucille = ts.user(search='Lucille')[0]

compositebuild = ts.compositebuild(data={
  composite: composite['id'],
  aggregationlayer: region['id'],
  owner: lucille['id'],
})

# Trigger the composite build (will require user confirmation).
ts.build(compositebuild)
```

## Train and run classifiers

To run a classifier, first some training data has to be ingested and assigned
to a classifier object. With the training data, the classifier can be trained
and then applied to a predicted layer object. These steps are outlined below.

### Ingest training data

Training data polygons can be ingested using an utility function. The training
data needs to be provided as a polygon shapefile layer. The function has the
following required arguments:

- *traininglayer*: The training layer to which to add the training samples.
- *image*: The training data is assumed to be "drawn" over a scene or a composite.
  So either a scene or a composite is required.
- *shapefile*: An absoulte path to a shapefile.
- *class_column*: The name of the column in the attribute table that contains
  the training class. Either an integer or a string column.
- *valuemap*: A dictionary with class names as keys and class
  values as integers. If integers are found in the class_column, the dict will
  be used to extract class names and vice versa.

Optinally, a `date_column` input can be specified to ingest training samples
with a date stamp attached to it. The date column should either be a text column
with a `YYYY-MM-DD` structure, or a proper date column.

There is one optional argument to reset the current set of training samples. If
`reset=True` is passed as an argument, all current training samples in the layer
will be permanently deleted.

The ingest function can be called as follows. A user confirmation will be
requested before deleting or writing data.

```python
# Get a training layer.
traininglayer = ts.traininglayer(search='Landcover')[0]
# Get the composite over which the training was "drawn". This could also be a
# scene, both are accepted.
composite = ts.composite(min_date_after='2017-03-01', min_date_before='2018-03-31')[0]
# Set path, column name and valuemap.
shp_path = '/path/to/shapefile.shp'
class_column = 'high_or_low'
valuemap = {'high': 1, 'low': 2}
# Upload training samples, deleting the current set of training samples.
response = ts.ingest(traininglayer, scene, shp_path, 'name', valuemap, reset=True)
```

### Train a Classifier

To train a classifier, a training layer has to be assigned to it. This can
happen upon creation, or the training layer can be assigned or updated  classifier after
creation

```python
# Get a classifier.
classifier = ts.classifier(search='Landcover')[0]
# Assign a training layer to it (optional if the classifier already has an
# traininglayer assigned to it).
traininglayer = ts.traininlayer(search='Landcover training data')[0]
ts.classifier(id=classifier['id'], data={'traininglayer': traininglayer['id']})
# Trigger training of the classifier.
ts.train(classifier)
```

### Predict a layer

```python
# Get a predicted layer (contains info about area and classifier to use).
predictedlayer = ts.predictedlayer()[0]
# Trigger prediction of the layer.
ts.predict(predictedlayer)
```

## Export data
A layer can be exported in one line. The input is a composite or a scene and a
formula to evaluate against the data layer. A region also needs to be specified
to define over which area to export, and a path to a file that will be newly
created or overwritten by the export function. The zoom level at which to run
the export can be specified with the optional `tilez` argument. The default zoom
level is `14`.

The region input can either be an aggregationlayer region, or a single
aggregationarea polygon from the region. In the case of the aggregationlayer
input, the extent of the entire layer will be used as export target.

If the target path is not provided, the function will return a numpy array.

The export function has an argument `clip_to_geom`, if it is set to `True`, the
target raster is clipped against the region geometry.

The rasterization mode can be set using the `all_touched` option.

The following example exports NDVI of a march composite over Ethiopia.

```python
# Get a formula.
formula = ts.formula(search='NDVI')[0]
# Get a scene or a composite for export.
composite = ts.composite(min_date_after='2017-03-01', min_date_before='2018-03-31')[0]
# Get region over which to export.
region = ts.region(search='Ethiopia')[0]
# Specify the local path for the target file.
target = '/path/to/newfile.tif'
# Specify the export zoom level (default is 14).
zoom = 8
# Export the data of the formula result evaluated on the composite over the region.
ts.export(region, composite, formula, target, zoom)
# Get the data as numpy array.
target = None
result = ts.export(region, composite, formula, target, zoom)
# Clip the raster against the input area geometry, where all touched pixels are
# included in the rasterization.
clip_to_geom = True
result = ts.export(region, composite, formula, target, zoom, clip_to_geom, all_touched=True)
```

## Aggregation
The aggregation api can be called by passing a composite or scene, a formula and
an aggregation area to the aggregation function.

Three optional arguments are available: `grouping`, which determines the grouping
parameter, `zoom` which determines the zoom level at which the aggregation
shall be computed, and `synchronous` which determines if the aggregation is
requested in synchronous or asynchronous mode. Defaults to `True`.

Note that if the aggregation values have not been already precomputed, the
computation is requested. In an asynchronous request, the aggregation value has
to be requested a second time after the initial request to get the result. The
status of the object will determine if the aggregation value has been precomputed
successfully.

The following creates a list of aggregation values with one entry for each
aggregation area in a region.

```python
formula = ts.formula(search='NDVI')[0]
# Get a scene or a composite for export.
composite = ts.composite(min_date_after='2017-03-01', min_date_before='2018-03-31')[0]
# Get region over which to export.
region = ts.region(search='Ethiopia')[0]
# Loop through aggregation areas in region.
aggregates = []
for area_id in region['aggregationareas']:
    # Get aggregation area.
    area = ts.area(area_id)
    # Compute aggregate (triggers async computation if not precomputed).
    agg = ts.aggregate(area, composite, ndvi)
    aggregates.append(agg)
```

### Regional aggregates
In some cases, comparing aggregates over regions might be desireable. Tesselate
allows computing regional aggregates. The value count result endpoint returns
the necessary internal statistics to compute "averages over averages" in a
mathematically exact way.

To get the regional statistics over a list of valuecount results (as obtained in
the example above), use the regional aggregate function as follows

```python
# The regional aggregate function takes a list of value count results and
# returns the regional statistics.
>>> regional_aggregate = ts.regional_aggregate(aggregates)
>>> print(regional_aggregate)
{
  "min": 0.599244875943905,
  "std": 0.017285077465624056,
  "mean": 0.8746274871261831,
  "max": 0.926344086021505
}
```

### Z-Scores based on regional aggregates
The regional aggregates can be used to create grouping parameters that compute
z-score values based on the average and standard deviation of the regional
aggregates.

Tesselate has a function to create the grouping parameter needed to request
z-scores through the aggregation endpoint. The following example uses the data
from the snippets above to request regional z-score value counts.

```python
# Get grouping parameter.
z_scores = ts.z_scores_grouping(regional_aggregate['mean'], regional_aggregate['std'])

# Re-compute aggregates using the z-score breaks.
z_aggregates = []
for area_id in region['aggregationareas']:
    area = ts.area(area_id)
    z_aggregates.append(ts.aggregate(area, composite, ndvi, z_scores))
```

## WMTS
With the `wmtslayer` endpoint, one can configure raster layers that will show
up in the WMTS endpoint of Tesselo.

The endpoint is an endpoint compliant with the [OGC WMTS](https://www.opengeospatial.org/standards/wmts)
standard. It can be used to include Tesselo data in many different software
packages, including QGis or ArcGIS.

The url for the WMTS service is the following:

```
https://api.tesselo.com/wmts/
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
