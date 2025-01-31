"""
Template tags for displaying icons.
"""

from django import template

register = template.Library()


@register.inclusion_tag("manager/fa6_icon.html")
def fa6_icon(name, style_prefix="fa-solid", title=None):
    """Returns a HMTL snippet which generates an fontawesome 6 icon.

    Parameters:

        style_prefix: str
            'fa-solid' (default) for solid icons, 'fa-regular' for regular icons
    """
    return {
        "classes": f"fa-{name} {style_prefix}",
        "title": title,
    }
