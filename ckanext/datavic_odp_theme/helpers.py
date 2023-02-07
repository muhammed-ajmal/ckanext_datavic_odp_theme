from __future__ import annotations

import json
import base64
import logging
from typing import Any, Optional
from datetime import datetime

from sqlalchemy import func
from dateutil.parser import ParserError, parse as parse_date

import ckan.plugins.toolkit as tk
import ckan.model as model

from ckanext.toolbelt.decorators import Collector


helper, get_helpers = Collector().split()
log = logging.getLogger(__name__)

CONFIG_DTV_FQ = "ckanext.datavicmain.dtv.supported_formats"
DEFAULT_DTV_FQ = [
    "wms",
    "shapefile",
    "zip (shp)",
    "shp",
    "kmz",
    "geojson",
    "csv-geo-au",
    "aus-geo-csv",
]


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
def format_list():
    """Return a list of all available resources on portal"""

    query = (
        model.Session.query(model.Resource.format)
        .filter(model.Resource.state == model.State.ACTIVE)
        .group_by(model.Resource.format)
        .order_by(func.lower(model.Resource.format))
    )

    return [resource.format for resource in query if resource.format]


@helper
def hotjar_tracking_enabled():
    return tk.asbool(tk.config.get("ckan.tracking.hotjar_enabled", False))


@helper
def monsido_tracking_enabled():
    return tk.asbool(tk.config.get("ckan.tracking.monsido_enabled", False))


@helper
def get_hotjar_hsid():
    return tk.config.get("ckan.tracking.hotjar.hjid", None)


@helper
def get_hotjar_hjsv():
    return tk.config.get("ckan.tracking.hotjar.hjsv", None)


@helper
def get_monsido_domain_token():
    return tk.config.get("ckan.tracking.monsido.domain_token", None)


@helper
def get_parent_site_url():
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
def get_gtm_code():
    # To get Google Tag Manager Code
    gtm_code = tk.config.get("ckan.google_tag_manager.gtm_container_id", False)
    return str(gtm_code)

@helper
def featured_resource_preview(package):
    # To get a featured preview for the dataset
    featured_preview = None
    if package.get("nominated_view_resource", None):
        try:
            resource_view = toolkit.get_action("resource_view_list")(
                {}, {"id": package["nominated_view_resource"]}
            )[0]
            resource = toolkit.get_action("resource_show")(
                {}, {"id": resource_view["resource_id"]}
            )
            featured_preview = {"preview": resource_view, "resource": resource}
        except tk.ObjectNotFound:
            pass
    return featured_preview

@helper
def get_google_optimize_id():
    return tk.config.get("ckan.google_optimize.id", None)

@helper
def get_digital_twin_resources(pkg_id: str) -> list[dict[str, Any]]:
    """Select resource suitable for DTV(Digital Twin Visualization).

    Additional info:
    https://gist.github.com/steve9164/b9781b517c99486624c02fdc7af0f186
    """
    supported_formats = {
        fmt.lower() for fmt in tk.aslist(tk.config.get(CONFIG_DTV_FQ, DEFAULT_DTV_FQ))
    }

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
    return toolkit.url_for(
        "vic_odp.dtv_config", encoded=encoded, embedded=embedded, _external=True
    )


@helper
def historical_resources_list(resources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    resources_history: dict[str, dict[str, Any]] = {}

    for idx, resource in enumerate(resources):
        resource["_key"] = _key = date_str_to_timestamp(
            resource.get("period_start", "")
        ) or int(f"9999999999{idx}")

        resources_history[str(_key)] = resource

    return sorted(resources_history.values(), key=lambda res: res["_key"], reverse=True)


@helper
def is_historical() -> bool:
    return tk.g.action == "historical"


@helper
def date_str_to_timestamp(date: str) -> Optional[int]:
    """Parses date string and return it as a timestamp integer"""
    try:
        date_obj: datetime = parse_date(date)
    except (ParserError, TypeError) as e:
        return log.error("Eror parsing date from %s", date)

    return int(date_obj.timestamp())


@helper
def is_other_license(pkg_dict: dict[str, Any]) -> bool:
    return pkg_dict.get("license_id") in ["other", "other-open"]
