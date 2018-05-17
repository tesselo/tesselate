from setuptools import find_packages, setup


def get_version():
    with open('tesselate/__init__.py', 'r') as init:
        for line in init.readlines():
            if line.startswith('__version__'):
                version = line.split(' = ')[1].rstrip()
                return version.split("'")[1]


setup(
    name='tesselate',
    version=get_version(),
    url='https://github.com/tesselo/tesselate',
    author='Daniel Wiesmann',
    author_email='daniel@tesselo.com',
    description='Tesselo Python SDK',
    license=None,
    packages=find_packages(exclude=('tests', )),
    include_package_data=True,
    install_requires=[
        'requests>=2.18.4',
        'Django>=2.0',
        'django-raster>=0.6',
    ],
)
