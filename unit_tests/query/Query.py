#!/usr/bin/python3 -S
# -*- coding: utf-8 -*-
import unittest
import json
from unit_tests import configure

from maestro.query import Query


class MyQuery(Query):
    pass


class TestQuery(unittest.TestCase):

    def test_init_(self):
        my_query = MyQuery()
        print('\n', my_query)


if __name__ == '__main__':
    # Unit test
    configure.run_tests(TestQuery, failfast=True, verbosity=2)
