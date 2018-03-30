from radar.radar import Radar
from radar import fields
from radar.query import Query
from radar.action import Action
from radar.record import Record
from radar.interface import Interface
from radar.union import Union
from radar import utils
from radar.exceptions import QueryErrors, ActionErrors, RecordIsNull

'''

Radar ->
Query+Action (records[requested], **params)
Record (query, fields[requested], index, **params)
Field (query, record, fields[requested_within], index[record index], **params)

'''
