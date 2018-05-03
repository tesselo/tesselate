# Tesselate - Tesselo's Python SDK

Copyright &copy; 2018 Tesselo, all rights reserved.

## Quickstart

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
ts.authenticate('lucille_bluth', 'shawnparmegian')
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

## Testing

To run the test, install mock with `pip install mock` and run tests with

    python -m unittest discover

To see test coverage, install coverage with `pip install coverage` and get
coverage with

    coverage run -m unittest discover
    coverage report -m --include=tesselate/*
