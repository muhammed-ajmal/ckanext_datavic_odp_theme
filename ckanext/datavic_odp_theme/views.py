from flask import Blueprint

import ckan.lib.helpers as h
import ckan.views.group as group
import ckan.plugins.toolkit as toolkit

_ = toolkit._
abort = toolkit.abort
NotAuthorized = toolkit.NotAuthorized
vic_odp = Blueprint('vic_odp', __name__)

FORBIDDEN_ACCESS = 403

def vic_groups_list(id):
    return h.redirect_to('dataset.read', id=id)

def vic_activity(id:str, offset:int=0):
    """ Raise and redirect to 403 if unauthorized
    :param id: organization name or id
    :param offset: offset
    :returns: redirect to 403 if not allowed view activity streams
    """
    try:
        return group.activity(id, offset=offset, group_type="organization", is_organization=True)
    except NotAuthorized:
        abort(FORBIDDEN_ACCESS, _('Unauthorized Access'))


vic_odp.add_url_rule( u'/dataset/groups/<id>', view_func=vic_groups_list)
vic_odp.add_url_rule( '/organization/activity/<id>/<int:offset>', 
                     methods=['GET'], view_func=vic_activity)