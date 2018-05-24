import copy


class ProcessResult(object):
    """
    base class for summing and processing a result document.
    the save() method is a stub which is overridden by a specific subclass to provide the ORM query for the actual save
    """
    def __init__(self, initial_data={}):
        self.storage_sum = copy.deepcopy(initial_data)
        self.extra_data = {}

    def add_entry(self, storage_id, size_in_bytes):
        if not storage_id in self.storage_sum:
            self.storage_sum[storage_id] = float(size_in_bytes)/1024.0**3
        else:
            self.storage_sum[storage_id] += float(size_in_bytes)/1024.0**3

    def combine(self, other):
        """
        adds the contents of another ProcessResult and returns the result
        :param other: other ProcessResult object
        :return: new ProcessResult object containing the combined objects' sums
        """
        rtn = ProcessResult()
        rtn.extra_data = self.extra_data
        rtn.storage_sum = copy.deepcopy(self.storage_sum)

        for storage_id, size_in_gb in other.storage_sum.items():
            if not storage_id in self.storage_sum:
                rtn.storage_sum[storage_id] = size_in_gb
            else:
                rtn.storage_sum[storage_id] += size_in_gb
        return rtn

    def __str__(self):
        return "{0}".format(self.storage_sum)

    def save(self,**kwargs):
        """
        saves the contents of the ProcessResult to a series of data model entries, one for each storage
        :return: the number of rows saved
        """
        pass

    def to_json(self,**kwargs):
        """
        returns a json representation of the data
        :return:
        """
        import json
        return json.dumps(self.storage_sum)