try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
        'description': 'pk-server: server daemon for running and accessing services via shared-secret port-knocking protocol',
    'author': 'Anson Rosenthal',
    'url': 'https://github.com/anrosent/pk-server.git',
    'download_url': 'https://github.com/anrosent/pk-server.git',
    'author_email': 'anson.rosenthal@gmail.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['pk'],
    'scripts': [],
    'name': 'pk-server'
}

setup(**config)
