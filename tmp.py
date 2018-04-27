import tesselate as ts

ts.client.authenticate('daniel', 'manimatter23')

base_path = '/home/tam/Desktop'

area = ts.region(search='Ethiopia')[0]
composite = ts.composite(year='2018')[2]

ndvi = ts.formula(search='NDVI')[0]
ts.export(area, composite, ndvi, base_path)

rgb = ts.formula(search='RGB')[0]
ts.export(area, composite, rgb, base_path)
