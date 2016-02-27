from django.db import models
from django.utils import html
import logging

logger = logging.getLogger(__name__)


class GridMetadataFields(models.Model):
    grid_field_name = models.CharField(max_length=255, help_text=html.escape('The name of the metadata field to set in The Grid'))
    format_string = models.CharField(max_length=4096,
                                     help_text=html.escape('''The value to set.  {vs_field_value} and {frame_number} will be substituted.''')
                                     )
    vs_field = models.CharField(max_length=255, blank=True,
                                help_text=html.escape('Read the value of this metadata field and substitute it in to format_string as {vs_field_value}'))
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
        from vidispine.vs_item import VSItem

        format_params = kwargs
        if vsitem is not None:
            if not isinstance(vsitem, VSItem):
                raise TypeError("GridMetadataFields.real_value must be passed a populated VSItem")
            if self.vs_field != "":
                format_params['vs_field_data'] = vsitem.get(self.vs_field)
            else:
                logger.warning("No vs_field set for '{0}'".format(unicode(self)))
        return self.format_string.format(format_params)

    class Meta:
        ordering = ['type','grid_field_name']

