class Members(object):
    def _getmembers(self):
        mro = self.__class__.__mro__
        mro_len = len(mro) - 3  # 3 = object, Members, Query
        for x in range(mro_len):
            for items in mro[mro_len - x - 1].__dict__.items():
                yield items
