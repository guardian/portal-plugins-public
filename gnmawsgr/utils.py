from portal.plugins.gnmawsgr import archive_test_value, restoring_test_value, archiving_test_value

def _find_group(groupname,meta):
    if not 'group' in meta:
        return None

    for g in meta['group']:
        if g['name'] == groupname:
            return g
        _find_group(groupname,g)

def metadataValueInGroup(groupname, mdkey, meta):
    if not isinstance(meta, list):
        meta = [meta]
    for item_data in meta:
        if 'metadata' in item_data:
            data_root = item_data['metadata']
        else:
            data_root = item_data
            
        for ts in data_root['timespan']:
            group = _find_group(groupname, ts)
            if group is None:
                raise ValueError("Could not find group {0}".format(groupname))
            for f in group['field']:
                if f['name'] == mdkey:
                    rtn = map(lambda x: x['value'],f['value'])
                    if len(rtn)==1:
                        return rtn[0]
                    else:
                        return rtn
    raise ValueError("Could not find metadata key {0}".format(mdkey))


def item_is_archived(item_metadata):
    """
    Is the given item in deep archive?
    :param itemref: Portal item metadata dictionary
    :return: True if the item is in deep archive, False otherwise
    """
    return metadataValueInGroup('ExternalArchiveRequest', 'gnm_external_archive_external_archive_status', item_metadata) == archive_test_value


def item_is_restoring(item_metadata):
    """
    Has a restore been requested for the item?
    :param itemref: Portal item metadata dictionary
    :return: True if the item is awaiting restore, False otherwise
    """
    return metadataValueInGroup('ExternalArchiveRequest', 'gnm_external_archive_external_archive_request', item_metadata) == restoring_test_value


def item_will_be_archived(item_metadata):
    """
    Has a restore been requested for the item?
    :param itemref: Portal item metadata dictionary
    :return: True if the item is awaiting restore, False otherwise
    """
    return metadataValueInGroup('ExternalArchiveRequest', 'gnm_external_archive_external_archive_request', item_metadata) == archiving_test_value
