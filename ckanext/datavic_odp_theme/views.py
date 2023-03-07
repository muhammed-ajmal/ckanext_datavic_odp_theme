import random

from flask import Blueprint

import ckan.lib.helpers as h
from ckan.common import request
import ckan.plugins.toolkit as toolkit
import ckan.views.dataset as dataset

NotFound = toolkit.ObjectNotFound
vic_odp = Blueprint("vic_odp", __name__)
PERCENTAGE_OF_CHANCE = 0.5


def vic_groups_list(id):
    return h.redirect_to("dataset.read", id=id)


def redirect_read(id:str):
    """
    redirect randomly if no_preview not provided
    """
    try:
        pkg_dict = toolkit.get_action("package_show")({}, {"id": id})
    except (NotFound):
        return dataset.read("dataset", id)

    preview_enabled = int(random.random() < PERCENTAGE_OF_CHANCE)
    no_preview = request.params.get("no_preview")

    if pkg_dict.get("nominated_view_resource") not in ["", None]:

        if no_preview is None and preview_enabled:
            return toolkit.h.redirect_to(
                f"/dataset/{id}?no_preview={preview_enabled}")

    return dataset.read("dataset", id)


vic_odp.add_url_rule("/dataset/groups/<id>", view_func=vic_groups_list)
