class ProcessResult(object):
    """
    base class for summing and processing a result document.
    the save() method is a stub which is overridden by a specific subclass to provide the ORM query for the actual save
    """
    def __init__(self):
        self.storage_sum = {}

    def add_entry(self, storage_id, size_in_bytes):
        if not storage_id in self.storage_sum:
            self.storage_sum[storage_id] = float(size_in_bytes)/1024.0**3
        else:
            self.storage_sum[storage_id] += float(size_in_bytes)/1024.0**3

    def __str__(self):
        return "{0}".format(self.storage_sum)

    def save(self,**kwargs):
        """
        saves the contents of the ProcessResult to a series of data model entries, one for each storage
        :return: the number of rows saved
        """
        pass
