from setuptools import setup

version = "0.3"

setup(
    name='tin2dem',
    version=version,
    description="LandXML to DEM tiff converter",
    author='Alexey Dolinenko',
    author_email="dolinenko@gmail.com",
    url='https://github.com/lekks/tin2dem',
    classifiers=[  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Programming Language :: Python'
    ],
    keywords="DEM LandXML",  # Separate with spaces
    packages=['tin2dem'],
    package_data={
        "tin2dem": ["*.cl"],
    },
    install_requires=open('requirements.txt').read().split(),
    entry_points={
        'console_scripts':
            ['tin2dem=tin2dem.main:cli']
    }
)
