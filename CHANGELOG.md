Tesselate Release Notes
=======================

0.3.1
-----
- Fixed asynchronous mode for aggregation utility.

0.3
---
Breaking change: the data model for training samples has changed. Training
samples are no longer assigned to a classifier directly. Instead, they are
assigned to a *training layer* and then the layer as a whole is assigned to the
classifier. This improves training data management. It also prevents having
"free floating" training samples that are not associated to anything.

Other changes:

- Fixed nodata bug on RGB exports.
- Added option to force object deletion without user confirmation.

0.2.2
-----
- Fixed zoomlevel bug on export, zoomlevel specification was not working.
- Fixed export of areas that contain empty tiles.

0.2.1
-----
Fixed bug in compositebuild trigger.

0.2.0
-----
First full stack implementation. Tesselate can now be used to create composites,
upload training data, train an algorithm, predict a layer and export the result.
I.e. the full workflow from zero to predicted layer is now covered!

In detail, the following changes:
- Added predicted layer endpoint.
- Added trigger functions for long running tasks: build composite, train
  classifier, predict layer.
- Created shapefile ingestor to upload trainig data.

0.1.2
-----
- Added possibility to manage permissions on objects.
- Added possibility to request user or group permission lists.
- Added unittests for auth and main dispatcher.
- Changed import method for tesselate functionality. Now use ``from tesselate import Tesselate``
  and then instantiate ``ts = Tesselate()``. The rest works the same way.
- Added experimental functionality for classify endpoints.
- Added create and update functionality to rest endpoints.

0.1.1
-----
- Fixed requests with custom grouping parameter.
- Fixed synchronous valuecount calculation.
- Changed ``base_path`` to ``file_path`` on export function. Setting the full
  filepath is more flexible than a base path with automatic naming.

0.1
---
- First version
- Endpoints for composites, formula, area, export and valuecounts.
- Automatic "loose" filter interpretation as kwargs on endpoints.
- Authentication either by setting token or logging in using credentials.
