from __future__ import annotations

import json
import base64
import random

from flask import Blueprint, jsonify

import ckan.lib.helpers as h
import ckan.views.api as api
import ckan.plugins.toolkit as tk
import ckan.views.dataset as dataset

from ckanext.datavic_odp_theme import helpers
from ckanext.datavic_odp_theme.views.historical import odp_historical
from ckanext.datavic_odp_theme.views.sitemap import odp_sitemap
from ckanext.datavic_odp_theme.views.group import odp_group

NotFound = tk.ObjectNotFound
PERCENTAGE_OF_CHANCE = 0.5
CONFIG_BASE_MAP = "ckanext.datavicmain.dtv.base_map_id"
DEFAULT_BASE_MAP = "vic-cartographic"

vic_odp = Blueprint("vic_odp", __name__)


@vic_odp.route("/dataset/groups/<id>")
def vic_groups_list(id):
    return h.redirect_to("dataset.read", id=id)


@vic_odp.route("/api/action/format_list")
def formats():
    return api._finish(200, helpers.format_list(), content_type="json")


def redirect_read(id: str):
    """
    redirect randomly if no_preview not provided
    """
    try:
        pkg_dict = tk.get_action("package_show")({}, {"id": id})
    except NotFound:
        return dataset.read("dataset", id)

    preview_enabled = int(random.random() < PERCENTAGE_OF_CHANCE)
    no_preview = tk.request.params.get("no_preview")

    if pkg_dict.get("nominated_view_resource") not in ["", None]:
        if no_preview is None and preview_enabled:
            return tk.h.redirect_to(f"/dataset/{id}?no_preview={preview_enabled}")

    return dataset.read("dataset", id)


def dtv_config(encoded: str, embedded: bool):
    try:
        ids: list[str] = json.loads(base64.urlsafe_b64decode(encoded))
    except ValueError:
        return tk.abort(409)
    base_url: str = (
        tk.config.get("ckanext.datavicmain.odp.public_url")
        or tk.config["ckan.site_url"]
    )

    catalog = []
    pkg_cache = {}

    for id_ in ids:
        try:
            resource = tk.get_action("resource_show")({}, {"id": id_})
            if resource["package_id"] not in pkg_cache:
                pkg_cache[resource["package_id"]] = tk.get_action("package_show")(
                    {}, {"id": resource["package_id"]}
                )

        except (tk.NotAuthorized, tk.ObjectNotFound):
            continue

        pkg = pkg_cache[resource["package_id"]]
        catalog.append(
            {
                "id": f"data-vic-embed-{id_}",
                "name": "{}: {}".format(pkg["title"], resource["name"] or "Unnamed"),
                "type": "ckan-item",
                "url": base_url,
                "resourceId": id_,
            }
        )

    return jsonify(
        {
            "baseMaps": {
                "defaultBaseMapId": tk.config.get(
                    CONFIG_BASE_MAP, DEFAULT_BASE_MAP
                )
            },
            "catalog": catalog,
            "workbench": [item["id"] for item in catalog],
            "elements": {
                "map-navigation": {"disabled": embedded},
                "menu-bar": {"disabled": embedded},
                "bottom-dock": {"disabled": embedded},
                "map-data-count": {"disabled": embedded},
                "show-workbench": {"disabled": embedded},
            },
        }
    )


vic_odp.add_url_rule("/dataset/groups/<id>", view_func=vic_groups_list)
vic_odp.add_url_rule(
    "/dtv_config/<encoded>/config.json",
    view_func=dtv_config,
    defaults={"embedded": False},
)
vic_odp.add_url_rule(
    "/dtv_config/<encoded>/embedded/config.json",
    view_func=dtv_config,
    defaults={"embedded": True},
)


def get_blueprints():
    # Check feature preview is enabled or not
    # If enabled add the redirect view for read pkg
    preview_redirect_enabled = tk.asbool(
        tk.config.get('ckan.dataset.preview_redirect', None)
        )
    if preview_redirect_enabled:
        vic_odp.add_url_rule( u'/dataset/<id>', view_func=redirect_read)

    return [odp_historical, odp_sitemap, odp_group, vic_odp]
