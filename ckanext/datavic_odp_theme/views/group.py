import logging

from flask import Blueprint

import ckan.plugins.toolkit as tk
import ckan.views.group as group

from ckanext.datavic_odp_theme.const import FORBIDDEN_ACCESS

log = logging.getLogger(__name__)
odp_group = Blueprint("odp_group", __name__)

@odp_group.route("/organization/activity/<id>/<int:offset>")
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