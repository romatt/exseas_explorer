#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements: list[str] = []

test_requirements = [
    "pytest>=3",
]

setup(
    author="Roman Attinger",
    author_email="roman.attinger@env.ethz.ch",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="INTEXseas Extreme Seasons Explorer",
    install_requires=requirements,
    license="BSD license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="exseas_explorer",
    name="exseas_explorer",
    packages=find_packages(include=["exseas_explorer", "exseas_explorer.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/romatt/exseas_explorer",
    version="0.1.0",
    zip_safe=False,
)
