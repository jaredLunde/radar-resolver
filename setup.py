#!/usr/bin/python3 -S
import os
import uuid
from setuptools import setup
from pkgutil import walk_packages


PKG = 'radar'
PKG_NAME = 'radar-resolver'
PKG_VERSION = '0.2.10'

pathname = os.path.dirname(os.path.realpath(__file__))

def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return (line for line in lineiter if line and not line.startswith("#"))

install_reqs = parse_requirements(pathname + "/requirements.txt")


def find_packages(prefix=""):
    path = [prefix]
    yield prefix
    prefix = prefix + "."
    for _, name, ispkg in walk_packages(path, prefix):
        if ispkg:
            yield name


setup(
    name=PKG_NAME,
    version=PKG_VERSION,
    description='A python resolver for react-radar Queries and Actions',
    author='Jared Lunde',
    author_email='jared.lunde@gmail.com',
    url='https://github.com/jaredlunde/radar-resolver',
    license="MIT",
    install_requires=list(install_reqs),
    packages=list(find_packages(PKG))
)
