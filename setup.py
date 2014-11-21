try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Monitor files at the beamline and perform actions when they change',
    'author': 'David J. Vine',
    'url': 'github.com/djvine',
    'download_url': 'github.com/djvine/beamon',
    'author_email': 'djvine@gmail.com',
    'version': '0.1',
    'install_requires': [],
    'data_files': [('beamon', ['beamon/xrayref.db'])],
    'packages': ['beamon'],
    'scripts': [],
    'name': 'beamon'
}

setup(**config)
