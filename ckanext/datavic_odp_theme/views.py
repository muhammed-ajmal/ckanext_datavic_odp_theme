from flask import Blueprint

import ckan.lib.helpers as h

vic_odp = Blueprint('vic_odp', __name__)


def vic_groups_list(id):
    return h.redirect_to('dataset.read', id=id)


vic_odp.add_url_rule( u'/dataset/groups/<id>', view_func=vic_groups_list)
