from django.urls import reverse
from topobank.manager.models import Topography


def prepare_context(context):
    if "extra_tabs" not in context:
        context["extra_tabs"] = []
    for tab in context["extra_tabs"]:
        tab["active"] = False


def add_generic(context, d):
    prepare_context(context)
    context["extra_tabs"] += [d]


def add_surface(context, surface):
    add_generic(
        context,
        {
            "title": f"{surface.label}",
            "icon": "layer-group",
            "icon_style_prefix": "fa",
            "href": f"{reverse('ce_ui:surface-detail', kwargs=dict(pk=surface.pk))}",
            "active": True,
            "login_required": False,
            "tooltip": f"Properties of digital surface twin '{surface.label}'",
        },
    )


def add_topography(context, topography):
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
    topography_tab = {
        "title": f"{topography.name}",
        "icon": "microscope",
        "icon_style_prefix": "fa",
        "href": reverse("ce_ui:topography-detail", kwargs=dict(pk=topography.pk)),
        "active": True,
        "login_required": False,
        "tooltip": f"Properties of measurement '{topography.name}'",
    }
    if next is not None:
        topography_tab["href_next"] = reverse(
            "ce_ui:topography-detail", kwargs=dict(pk=next.pk)
        )
    if previous is not None:
        topography_tab["href_previous"] = reverse(
            "ce_ui:topography-detail", kwargs=dict(pk=previous.pk)
        )
    add_generic(context, topography_tab)
