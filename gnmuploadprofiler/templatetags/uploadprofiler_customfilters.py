from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter("time_display")
def time_display(value):
    try:
        number=float(value)
    except ValueError:
        return value

    hours=0
    minutes=0
    seconds=0

    if number<60:
        seconds=number
    else:
        minutes=int(number/60.0)
        seconds=number-(minutes*60)

    if minutes>60:
        hours=int(minutes/60.0)
        minutes=minutes-(hours*60)

    if hours>0:
        return u'{h} hours, {m} minutes, {s:.1f} seconds'.format(h=hours,m=minutes,s=seconds)
    elif minutes>0:
        return u'{m} minutes, {s:.1f} seconds'.format(m=minutes,s=seconds)
    else:
        return u'{s:.1f} seconds'.format(s=seconds)