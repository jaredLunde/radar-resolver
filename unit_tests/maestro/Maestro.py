#!/usr/bin/python3 -S
# -*- coding: utf-8 -*-
import unittest
import json
from unit_tests import configure

from maestro.maestro import Maestro
from maestro.query import Query


payload = payload = '''
{
    "queries": [
        {
            "UserProfileQuery": {
                "params": {
                    "username": "jared"
                },
                "nodes": {
                    "User":  [
                        "uid",
                        "username",
                        {
                            "friends": [
                                "uid",
                                "username"
                            ]
                        }
                    ]
                }
            }
        }
    ],
    "mutations": [
        {
            "AddUser": {
                "payload": {
                    "username": "abc",
                    "password": "abc1234567",
                    "email": "abc@gmail.com"
                }
            }
        }
    ]
}
'''


class UserProfileQuery(Query):
    pass


class TestQuery(unittest.TestCase):

    def test_init_(self):
        maestro = Maestro()
        maestro.install_query(UserProfileQuery)
        print('\n', maestro.resolve(payload))


if __name__ == '__main__':
    # Unit test
    configure.run_tests(TestQuery, failfast=True, verbosity=2)
