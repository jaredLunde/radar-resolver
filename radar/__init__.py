from radar.radar import Radar
from radar import fields
from radar.query import Query
from radar.action import Action
from radar.node import Node
from radar.interface import Interface
from radar.union import Union
from radar import utils
from radar.exceptions import QueryErrors, ActionErrors, NodeIsNull

'''

Radar ->
Query+Action (nodes[requested], **params)
Node (query, fields[requested], index, **params)
Field (query, node, fields[requested_within], index[node index], **params)

'''
