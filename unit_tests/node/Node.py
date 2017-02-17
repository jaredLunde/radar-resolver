#!/usr/bin/python3 -S
# -*- coding: utf-8 -*-
import unittest
from unit_tests import configure

from maestro.node import Node
from maestro.fields import *


class MyNode(Node):
    my_string = String()
    my_int = Int()


class TestNode(unittest.TestCase):

    def test_init_(self):
        my_node = MyNode()
        print('\n', my_node)
        print(my_node.to_dict())




if __name__ == '__main__':
    # Unit test
    configure.run_tests(TestNode, failfast=True, verbosity=2)
