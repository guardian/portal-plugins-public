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

@register.filter("proportion")
def proportion(value,divisor):
    frac=(float(value)/float(divisor))*100.0

    text_class=""
    if frac>=0 and frac<25:
        text_class="first_q"
    elif frac>=25 and frac<50:
        text_class="second_q"
    elif frac>=50 and frac<75:
        text_class="third_q"
    else:
        text_class="fourth_q"

    return mark_safe(u'<span class="{c}">{v:.0f}%</span>'.format(c=text_class,v=frac))