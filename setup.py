from setuptools import find_packages, setup

from utilities import __version__

setup(
    name='utilities',
    version=__version__,
    license='BSD',
    author='GNM',
    author_email='solutiondb@gmail.com',
    description='Utils lib for utils methods',
    url='https://github.com/xlash/utils',
    install_requires=['curtsies', 'decorator', 'python-dateutil', 'pyyaml', 'multiprocessing_logging'],
    packages=find_packages(),
)
