import tesselate as ts

ts.client.authenticate('daniel', 'manimatter23')

base_path = '/home/tam/Desktop'

region = ts.region(search='Ethiopia')[0]
composite = ts.composite(year='2018')[2]

ndvi = ts.formula(search='Chlorophyll')[0]
# ts.export(region, composite, ndvi, base_path)

# rgb = ts.formula(search='RGB')[0]
# ts.export(region, composite, rgb, base_path)

aggregates = []
for area_id in region['aggregationareas']:
    area = ts.area(area_id)
    aggregates.append(ts.aggregate(area, composite, ndvi))

regional_aggregate = ts.regional_aggregate(aggregates)
