from maestro.maestro import Maestro
from maestro import fields
from maestro.query import Query
from maestro.action import Action
from maestro.node import Node
from maestro import utils
'''
TEST MAESTRO:
from gomaestro.maestro import gomaestro_maestro; import json; print(json.dumps(gomaestro_maestro.resolve('{"queries": [{"UserProfileQuery": {}}, {"UserProfileQuery": {"params": {"username": "jared"}, "nodes": {"UserProfileSchema": ["username"]}}}]}'), indent=2))


TEST NODE TO JS:
from gomaestro.maestro.plugins.js_keys import *; from gomaestro.maestro.plugins.case import *; from gomaestro.maestro.nodes import UserProfileSchema; u = UserProfileSchema(); print(u.to_js(plugins=[recursive_keys_to_camelcase], indent=2))


Receives JSON encoded request:
{
    "queries": {
        "storeLabel": {
            "type": "QueryName"
            "params": {
                "p1": 1234,
                "p2": "pval"
            },
            "nodes": {
                "nodeLabel":  ["field1", "field2"]
            }
        }
    }
}

'''
