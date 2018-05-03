Tesselate Changelog
===================

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
