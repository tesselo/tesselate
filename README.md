Tesselate - Tesselo's Python SDK
================================

Copyright (c) 2018 Tesselo

Quickstart
----------

```python
from tesselate import Tesselate

ts = Tesselate()

ts.authenticate('lucille_bluth', '***')

ts.composite(min_date_0='2017-04-01', min_date_1='2018-03-31', interval='Monthly')
```

Testing
-------

To run the test, install mock with ``pip install mock`` and run tests with

    python -m unittest discover

To see test coverage, install coverage with ``pip install coverage`` and get
coverage with

    coverage run -m unittest discover
    coverage report -m --include=tesselate/*
