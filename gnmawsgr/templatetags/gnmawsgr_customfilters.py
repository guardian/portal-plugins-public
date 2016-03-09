from __future__ import division
from django import template
from django.utils.safestring import mark_safe
import portal.plugins.gnmawsgr.models as models
import logging

logger = logging.getLogger(__name__)
register = template.Library()


@register.filter("filesize_progress_graph")
def filesize_progress_graph(value):
    if not isinstance(value,models.RestoreRequest):
        logger.warning("filesize_progress_graph called with something that is not a RestoreRequest object")
        return value

    pct = value.currently_downloaded / value.filesize
    pct *= 100

    rtn = "<svg id=\"filesize_progress_graph\" class=\"filesize_progress_graph\">"
    rtn += '<rect width="{width}%" height="100%" style="fill:rgb({r},{g},{b});stroke-width:{stroke};stroke:rgb(0,0,0)"/>'.format(
        width=pct,
        r=220,
        g=0,
        b=0,
        stroke=1
    )
    rtn += "</svg>"
    return mark_safe(rtn)