import json
from collections import namedtuple


class AssetInfo(object):
    """
    Object to represent an asset entry in the media atom model.
    Provides a get_url() method to return a URL to the asset.
    """
    def __init__(self, version, id, assetType="video", platform="youtube"):
        self.version = version
        self.external_id = id
        self.assetType = assetType
        self.platform = platform

    def get_url(self):
        if self.platform.lower() == "youtube":
            return "https://www.youtube.com/watch?v={0}".format(self.external_id)
        else:
            raise ValueError("Unrecognised platform {0}".format(self.platform))


class AtomMessage(object):
    """
    Object that represents a parsed message from the media atom tool.
    Each proprty on the json object is accessible as a property on this object,
    for example:
      >> a = AtomMessage(content_string)
      >> a.description
      "atom description"

    Special properties are available for more complex objects:
     - posterImages - generator that yields poster images from the object
     - biggest_poster_image - finds the largest poster image specified and returns that

    """
    def __init__(self, jsonstring):
        """
        Initialises an instance with the data parsed from the given json string.
        Raises json exceptions if this is not valid.
        :param jsonstring:
        """
        if not isinstance(jsonstring,basestring):
            raise TypeError

        self._content = json.loads(jsonstring)

    def __getattr__(self, item):
        """
        Generic property getter. Raises ValueError if the property does not exist.
        :param item: proprty name to get
        :return: Value of the property or raises a ValueError
        """
        if not item in self._content:
            raise ValueError("We don't have a value for {0}".format(item))

        return self._content[item]

    @property
    def posterImages(self):
        """
        Generator to yield image_info objects of each poster image
        image_info objects support mimeType, file, dimensions and size properties.
        :return: yields image_info objects
        """
        image_info = namedtuple('image_info',"mimeType file dimensions size", verbose=False)

        for entry in self._content['posterImage']['assets']:
            yield image_info(entry['mimeType'], entry['file'], entry['dimensions'], entry['size'])

    def biggest_poster_image(self):
        """
        Finds the biggest poster image on the content and returns it.
        :return: image_info object for the biggest poster image, or None if no images are defined.
        """
        rtn = None

        for entry in self.posterImages:
            if rtn is None:
                rtn = entry
                continue
            if entry.size > rtn.size:
                rtn = entry

        return rtn

    @property
    def assets(self):
        """
        Generator to yield asset_info objects of each asset
        :return:
        """
        for entry in self._content['assets']:
            yield AssetInfo(entry['version'],entry['id'],entry['assetType'],entry['platform'])

    @property
    def latest_asset(self):
        """
        Returns the asset_info of the most recent asset, or None if there are no assets.
        :return: asset_info or None
        """
        rtn = None
        for asset in self.assets:
            if rtn is None:
                rtn = asset
                continue
            if asset.version > rtn.version:
                rtn = asset
        return rtn