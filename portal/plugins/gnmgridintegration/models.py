from django.db import models
from django.utils import html
import logging

logger = logging.getLogger(__name__)


class GridMetadataFields(models.Model):
    """
    This model represents a profile for setting metadata fields in the Grid for a captured image based on the Vidispine
    metadata of the Item that it was captured from.
    It supports either static strings or Vidispine field captures, one per output field, and also inserting the captured
    frame number
    """
    grid_field_name = models.CharField(max_length=255, help_text=html.escape('The name of the metadata field to set in The Grid'))
    format_string = models.CharField(max_length=4096,
                                     help_text=html.escape('''The value to set.  {vs_field_data} and {frame_number} will be substituted.''')
                                     )
    vs_field = models.CharField(max_length=255, blank=True,
                                help_text=html.escape('Read the value of this metadata field and substitute it in to format_string as {vs_field_data}'))
    type = models.IntegerField(choices=((1, 'ItemMetadata'),(2, 'RightsMetadata')),
                               help_text=html.escape('Should the field be set as item metadata or rights metadata?'))

    def __unicode__(self):
        if self.vs_field is not None and self.vs_field != "":
            return u'Set Grid field "{0}" from {1}'.format(self.grid_field_name, self.vs_field)
        else:
            return u'Set Grid field "{0}" from static string'.format(self.grid_field_name)

    def real_value(self, vsitem, **kwargs):
        """
        Returns the formatted string value for this metadata field
        :param vsitem: VSItem to look up data from.  If specified, then the {vs_field_data} substitution in
        self.format_string will be set to the value held in the field self.vs_field on this item.
        If this is not a VSItem or None, a TypeError will be raised.  If the field does not exist then the string 'None'
        will be substituted
        :param kwargs: Other format parameters to apply to the string
        :return: Formatted string
        """
        from gnmvidispine.vs_item import VSItem
        from pprint import pformat
        format_params = {}
        format_params.update(kwargs)
        if vsitem is not None:
            if not isinstance(vsitem, VSItem):
                raise TypeError("GridMetadataFields.real_value must be passed a populated VSItem")
            if self.vs_field != "":
                format_params['vs_field_data'] = vsitem.get(self.vs_field)
                logger.debug(u"got value {0} for field {1}".format(unicode(format_params['vs_field_data']), self.vs_field))
            else:
                logger.warning(u"No vs_field set for '{0}'".format(unicode(self)))
        logger.debug(pformat(format_params))
        return self.format_string.format(**format_params)

    class Meta:
        ordering = ['type','grid_field_name']


class GridCapturePreset(models.Model):
    """
    In production use you probably would not want to capture every image snapped in the picker to the Grid.
    This model represents a metadata profile that, if matched, will allow the image to be sent on.
    """
    vs_field = models.CharField(max_length=256)
    field_value_regex = models.CharField(max_length=2048)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return u'{0} matches {1}'.format(self.vs_field,self.field_value_regex)

    class Meta:
        ordering = ['vs_field', 'field_value_regex']

    def should_trigger(self, item):
        """
        Returns TRUE if the given populated VSItem object matches this preset
        :param item: populated VSItem
        :return: True or False
        """
        import re
        if re.search(unicode(self.field_value_regex),
                     item.get(self.vs_field),
                     re.IGNORECASE|re.UNICODE) is not None:
            return True
        return False

    def info(self):
        """
        Returns a dict of json-friendly information about this profile
        :return: dict
        """
        return {
            'pk': self.pk,
            'desc': unicode(self),
            'field': unicode(self.vs_field),
            'value_regex': unicode(self.field_value_regex),
            'active': self.active
        }