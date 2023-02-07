from flask import Blueprint

import ckan.lib.helpers as h
import ckan.views.api as api

from ckanext.datavic_odp_theme import helpers
from ckanext.datavic_odp_theme.views.historical import odp_historical
from ckanext.datavic_odp_theme.views.sitemap import odp_sitemap

vic_odp = Blueprint("vic_odp", __name__)


@vic_odp.route("/dataset/groups/<id>")
def vic_groups_list(id):
    return h.redirect_to("dataset.read", id=id)


@vic_odp.route("/api/action/format_list")
def formats():
    return api._finish(200, helpers.format_list(), content_type="json")


def get_blueprints():
    return [odp_historical, odp_sitemap, vic_odp]
