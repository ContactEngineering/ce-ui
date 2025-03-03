from django.urls import reverse
from topobank.manager.models import Topography


def prepare_context(context):
    if "extra_tabs" not in context:
        context["extra_tabs"] = []
    for tab in context["extra_tabs"]:
        tab["active"] = False


def add_surface(context, surface):
    prepare_context(context)
    context["extra_tabs"] += [
        {
            "title": f"{surface.label}",
            "icon": "layer-group",
            "icon_style_prefix": "fa",
            "href": f"{reverse('ce_ui:surface-detail')}?surface={surface.pk}",
            "active": True,
            "login_required": False,
            "tooltip": f"Properties of digital surface twin '{surface.label}'",
        }
    ]


def add_topography(context, topography):
    prepare_context(context)
    next = (
        Topography.objects.filter(surface=topography.surface, pk__gt=topography.pk)
        .order_by("pk")
        .first()
    )
    previous = (
        Topography.objects.filter(surface=topography.surface, pk__lt=topography.pk)
        .order_by("pk")
        .last()
    )
    url = reverse("ce_ui:topography-detail")
    topography_tab = {
        "title": f"{topography.name}",
        "icon": "microscope",
        "icon_style_prefix": "fa",
        "href": f"{url}?topography={topography.pk}",
        "active": True,
        "login_required": False,
        "tooltip": f"Properties of measurement '{topography.name}'",
    }
    if next is not None:
        topography_tab["href_next"] = f"{url}?topography={next.pk}"
    if previous is not None:
        topography_tab["href_previous"] = f"{url}?topography={previous.pk}"
    context["extra_tabs"] += [topography_tab]
