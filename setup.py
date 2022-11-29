from setuptools import setup, find_packages


setup(
    name='phyengine',
    version='1.1',
    license='MIT',
    author="tacterex",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/tacterex/PhyEngine',
    keywords='phyengine',
)
