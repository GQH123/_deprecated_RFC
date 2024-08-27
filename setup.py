import os
from setuptools import find_packages, setup

setup(
    name="RFC",
    py_modules=["RFC"],
    version="3.0.0",
    description="Renatus' Fast Crawler V3",
    author="Renatus",
    packages=find_packages(),
    entry_points={
        # "console_scripts": [
        #     "rfc = RFC.user.main:main",
        # ],
    },
    install_requires=[],
    include_package_data=True,
)