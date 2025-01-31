from setuptools import setup, find_packages

setup(
    name='fastener_analysis',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pint',
        'pytest'
    ],
)
