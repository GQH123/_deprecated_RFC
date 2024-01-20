import os
from setuptools import find_packages, setup

setup(
    name="RFC",
    py_modules=["RFC"],
    version="0.0.1",
    description="Renatus' Fast Crawler",
    author="Renatus",
    packages=find_packages(),
    entry_points={
    },
    install_requires=[],
    include_package_data=True,
)