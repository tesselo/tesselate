from setuptools import find_packages, setup

setup(
    name='tesselate',
    version='0.1',
    url='https://github.com/tesselo/tesselate',
    author='Daniel Wiesmann',
    author_email='daniel@tesselo.com',
    description='Tesselo Python SDK',
    license=None,
    packages=find_packages(exclude=('tests', )),
    include_package_data=True,
    install_requires=[
        'requests>=2.18.4',
    ],
)
