

from __future__ import absolute_import, division, print_function
import os.path as op
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="geosea", # Replace with your own username
    version="2022.1.2.1",
    author="Florian Petersen and Katrin Hannemann",
    author_email="florian.petersen@ifg.uni-kiel.de",
    description="A processing package for seafloor geodesy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/flp-geo/geosea",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
