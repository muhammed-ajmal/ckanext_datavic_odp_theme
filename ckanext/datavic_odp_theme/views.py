import random

from flask import Blueprint

import ckan.lib.helpers as h
import ckan.views.group as group
import ckan.plugins.toolkit as tk
from ckan.common import request
import ckan.views.dataset as dataset

from ckanext.datavic_odp_theme.const import FORBIDDEN_ACCESS


NotFound = tk.ObjectNotFound
PERCENTAGE_OF_CHANCE = 0.5

vic_odp = Blueprint("vic_odp", __name__)


def vic_groups_list(id):
    return h.redirect_to("dataset.read", id=id)


def vic_organization_activity(id: str, offset: int = 0):
    """Redirect to 403 if unauthorized
    :param id: organization name or id
    :param offset: offset
    :returns: redirect to 403 if not allowed view activity streams
    """
    try:
        return group.activity(
            id, offset=offset, group_type="organization", is_organization=True
        )
    except tk.NotAuthorized:
        tk.abort(FORBIDDEN_ACCESS, tk._("Unauthorized Access"))


def redirect_read(id:str):
    """
    redirect randomly if no_preview not provided
    """
    try:
        pkg_dict = tk.get_action("package_show")({}, {"id": id})
    except (NotFound):
        return dataset.read("dataset", id)

    preview_enabled = int(random.random() < PERCENTAGE_OF_CHANCE)
    no_preview = request.params.get("no_preview")

    if pkg_dict.get("nominated_view_resource") not in ["", None]:

        if no_preview is None and preview_enabled:
            return tk.h.redirect_to(
                f"/dataset/{id}?no_preview={preview_enabled}")

    return dataset.read("dataset", id)


vic_odp.add_url_rule(u"/dataset/groups/<id>", view_func=vic_groups_list)
vic_odp.add_url_rule(
    "/organization/activity/<id>/<int:offset>", view_func=vic_organization_activity
)
