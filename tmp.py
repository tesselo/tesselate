from tesselate import Tesselo

tess = Tesselo()
tess.client.authenticate('daniel', 'manimatter23')

area = tess.area(search='Ethiopia')[0]
print('AREA\n', area)
#formula = tess.formula(search='NDVI')[0]
formula = tess.formula(search='RGB')[0]
print('FORMULA\n', formula)
composite = tess.composite(year='2018')[2]
print('COMPOSITE\n', composite)
#tess.export(area, composite, formula)


# https://tesselo.com/api/algebra/15/19649/15338.png?layers=B4=17946,B8=17950&formula=(B8-B4)%2F(B8%2BB4)&colormap=%7B%22continuous%22%3Atrue%2C%22range%22%3A%5B-1%2C1%5D%2C%22from%22%3A%5B215%2C48%2C39%5D%2C%22over%22%3A%5B255%2C255%2C191%5D%2C%22to%22%3A%5B26%2C152%2C80%5D%7D
# https://tesselo.com/api/algebra/15/19649/15338.tif?layers=r=17946,g=17945,b=17944&scale=0,4e3&alpha&enhance_brightness=1.6&enhance_sharpness=1.2&enhance_color=1.2&enhance_contrast=1.1
