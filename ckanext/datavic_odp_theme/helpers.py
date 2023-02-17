from __future__ import annotations

import logging
import json
import base64
from typing import Any, Optional

from sqlalchemy import func

import ckan.plugins.toolkit as tk
import ckan.model as model

from ckanext.toolbelt.decorators import Collector

from ckanext.datavic_odp_theme import config as conf, const


log = logging.getLogger(__name__)
helper, get_helpers = Collector().split()


@helper
def organization_list():
    org_list = tk.get_action("organization_list")({}, {})
    organizations = []
    for org in org_list:
        org_dict = tk.get_action("organization_show")({}, {"id": org})
        organizations.append(org_dict)

    return organizations


@helper
def group_list():
    return tk.get_action("group_list")({}, {"all_fields": True})


@helper
def format_list() -> list[str]:
    """Return a list of all available resources on portal"""

    query = (
        model.Session.query(model.Resource.format)
        .filter(model.Resource.state == model.State.ACTIVE)
        .group_by(model.Resource.format)
        .order_by(func.lower(model.Resource.format))
    )

    return [resource.format for resource in query if resource.format]


@helper
def hotjar_tracking_enabled() -> bool:
    return tk.asbool(tk.config.get("ckan.tracking.hotjar_enabled", False))


@helper
def monsido_tracking_enabled() -> bool:
    return tk.asbool(tk.config.get("ckan.tracking.monsido_enabled", False))


@helper
def get_hotjar_hsid() -> Optional[str]:
    return tk.config.get("ckan.tracking.hotjar.hjid")


@helper
def get_hotjar_hjsv() -> Optional[str]:
    return tk.config.get("ckan.tracking.hotjar.hjsv")


@helper
def get_monsido_domain_token() -> Optional[str]:
    return tk.config.get("ckan.tracking.monsido.domain_token")


@helper
def get_parent_site_url() -> str:
    return tk.config.get("ckan.parent_site_url", "https://www.data.vic.gov.au/")


@helper
def release_date(pkg_dict):
    """
    Copied from https://github.com/salsadigitalauorg/datavic_ckan_2.2/blob/develop/iar/src/ckanext-datavic/ckanext/datavic/plugin.py#L296
    :param pkg_dict:
    :return:
    """
    dates = []
    dates.append(pkg_dict["metadata_created"])
    for resource in pkg_dict["resources"]:
        if (
            "release_date" in resource
            and resource["release_date"] != ""
            and resource["release_date"] != "1970-01-01"
        ):
            dates.append(resource["release_date"])
    dates.sort()
    return dates[0].split("T")[0]


@helper
def get_gtm_container_id() -> Optional[str]:
    return tk.config.get("ckan.google_tag_manager.gtm_container_id")


@helper
def featured_resource_preview(package) -> Optional[dict[str, Any]]:
    """Return a featured resource preview if exists for a specific dataset"""
    featured_preview = None
    if package.get("nominated_view_resource"):
        try:
            resource_view = tk.get_action("resource_view_list")(
                {}, {"id": package["nominated_view_resource"]}
            )[0]
            resource = tk.get_action("resource_show")(
                {}, {"id": resource_view["resource_id"]}
            )
            featured_preview = {"preview": resource_view, "resource": resource}
        except tk.ObjectNotFound:
            pass
    return featured_preview


@helper
def get_google_optimize_id() -> Optional[str]:
    return tk.config.get("ckan.google_optimize.id")


@helper
def get_digital_twin_resources(pkg_id: str) -> list[dict[str, Any]]:
    """Select resource suitable for DTV(Digital Twin Visualization).

    Additional info:
    https://gist.github.com/steve9164/b9781b517c99486624c02fdc7af0f186
    """
    supported_formats: set[str] = conf.get_dtv_supported_formats()

    try:
        pkg = tk.get_action("package_show")({}, {"id": pkg_id})
    except (tk.ObjectNotFound, tk.NotAuthorized):
        return []

    if not pkg.get("enable_dtv", False):
        return []

    # Additional info #2
    if pkg["state"] != "active":
        return []

    acceptable_resources = {}
    for res in pkg["resources"]:
        if not res["format"]:
            continue

        fmt = res["format"].lower()
        # Additional info #1
        if fmt not in supported_formats:
            continue

        # Additional info #3
        if (
            fmt in {"kml", "kmz", "shp", "shapefile", "zip (shp)"}
            and len(pkg["resources"]) > 1
        ):
            continue

        # Additional info #3
        if fmt == "wms" and ~res["url"].find("data.gov.au/geoserver"):
            continue

        # Additional info #4
        if res["name"] in acceptable_resources:
            if acceptable_resources[res["name"]]["created"] > res["created"]:
                continue

        acceptable_resources[res["name"]] = res

    return list(acceptable_resources.values())


@helper
def url_for_dtv_config(ids: list[str], embedded: bool = True) -> str:
    """Build URL where DigitalTwin can get map configuration for the preview."""

    encoded = base64.urlsafe_b64encode(bytes(json.dumps(ids), "utf8"))
    return tk.url_for(
        "vic_odp.dtv_config", encoded=encoded, embedded=embedded, _external=True
    )


@helper
def is_resource_downloadable(resource: dict[str, Any]) -> bool:
    if (
        resource.get("has_views")
        or resource.get("url_type") == "upload"
        or resource["format"].upper() not in const.NOT_DOWNLOADABLE_FORMATS
    ):
        return True

    return False
