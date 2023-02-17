from __future__ import annotations

import ckan.plugins.toolkit as tk


CONFIG_BASE_MAP = "ckanext.datavicmain.dtv.base_map_id"
DEFAULT_BASE_MAP = "basemap-vic-topographic"

CONFIG_BASE_URL = "ckanext.datavicmain.odp.public_url"

CONFIG_PREVIEW_REDIRECT = "ckan.dataset.preview_redirect"
DEFAULT_PREVIEW_REDIRECT = False

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


def get_default_base_map() -> str:
    return tk.config.get(CONFIG_BASE_MAP, DEFAULT_BASE_MAP)


def get_base_url() -> str:
    return tk.config.get(CONFIG_BASE_URL) or tk.config["ckan.site_url"]


def get_preview_redirect() -> bool:
    return tk.asbool(tk.config.get(CONFIG_PREVIEW_REDIRECT, DEFAULT_PREVIEW_REDIRECT))


def get_dtv_supported_formats() -> set[str]:
    return {
        fmt.lower() for fmt in tk.aslist(tk.config.get(CONFIG_DTV_FQ)) or DEFAULT_DTV_FQ
    }
