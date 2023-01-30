from __future__ import annotations

import random

from flask import Blueprint, jsonify

import ckan.lib.helpers as h
from ckan.common import request
import ckan.plugins.toolkit as toolkit
import ckan.views.dataset as dataset

NotFound = toolkit.ObjectNotFound
vic_odp = Blueprint("vic_odp", __name__)
PERCENTAGE_OF_CHANCE = 0.5
CONFIG_BASE_MAP = "ckanext.datavicmain.dtv.base_map_id"
DEFAULT_BASE_MAP = "vic-topographic"


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

def dtv_config():
    embedded = toolkit.asbool(toolkit.request.args.get("embedded"))
    ids: list[str] = toolkit.request.args.getlist("resource_id")
    base_url: str = (
        toolkit.config.get("ckanext.datavicmain.odp.public_url")
        or toolkit.config["ckan.site_url"]
    )

    catalog = []
    pkg_cache = {}

    for id_ in ids:

        try:
            resource = toolkit.get_action("resource_show")({}, {"id": id_})
            if resource["package_id"] not in pkg_cache:
                pkg_cache[resource["package_id"]] = toolkit.get_action("package_show")(
                    {}, {"id": resource["package_id"]}
                )

        except (toolkit.NotAuthorized, toolkit.ObjectNotFound):
            continue

        pkg = pkg_cache[resource["package_id"]]
        catalog.append({
            "id": f"data-vic-embed-{id_}",
            "name": "{}: {}".format(
                pkg["title"],
                resource["name"] or "Unnamed"
            ),
            "type": "ckan-item",
            "url": base_url,
            "resourceId": id_
        })

    return jsonify({
        "version": "8.0.0",
        "initSources": [{
            "baseMaps": {
                "defaultBaseMapId": toolkit.config.get(
                    CONFIG_BASE_MAP, DEFAULT_BASE_MAP
                )
            },
            "catalog": catalog,
            "workbench": [item["id"] for item in catalog],
            "elements": {
                "map-navigation": {
                    "disabled": embedded
                },
                "menu-bar": {
                    "disabled": embedded
                },
                "bottom-dock": {
                    "disabled": embedded
                },
                "map-data-count": {
                    "disabled": embedded
                },
                "show-workbench": {
                    "disabled": embedded
                }
            }
        }]
    })

vic_odp.add_url_rule("/dataset/groups/<id>", view_func=vic_groups_list)
vic_odp.add_url_rule('/dtv_config', view_func=dtv_config)
