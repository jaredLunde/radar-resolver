import json
import random
from maestro.node import Node
from maestro.query import Query
from maestro.union import Union
from maestro.interface import Interface
from maestro.fields import String, Array, Int


class SearchInterface(Interface):
    preview_text = String(lambda f, n: f'Preview for {n.__NAME__}')


class PicturesNode(Node):
    uid = String(lambda f, n: 'xYzBzcdD', key=True)
    size = Array(lambda f, n: [400, 300])


class VideosNode(Node):
    uid = String(lambda f, n: 'xYzBzcdD', key=True)
    quality = String(lambda f, n: '240p')


class SearchUnion(Union):
    # Nodes
    picture = PicturesNode().implement(SearchInterface)
    video = VideosNode().implement(SearchInterface)
    # preview_text = String(lambda field, node: f'Preview for {node.__NAME__}')
    def __iter__(self):
        self.current = -1
        self.count = 6
        return self
    def __next__(self):
        self.current += 1
        if self.current == self.count:
            raise StopIteration
        else:
            return self
    @property
    def node_type(self):
        return random.choice(['picture', 'video'])


class SearchQuery(Query):
    results = SearchUnion(many=True)
    def apply(self, **params):
        pass


sq = SearchQuery()
print(json.dumps(sq.resolve(), indent=2))
