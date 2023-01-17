from flask import Blueprint

import ckan.lib.helpers as h
from ckan.common import request,config
import ckan.plugins.toolkit as toolkit
import ckan.views.dataset as dataset
import random

NotFound = toolkit.ObjectNotFound
vic_odp = Blueprint('vic_odp', __name__)


def vic_groups_list(id):
    return h.redirect_to('dataset.read', id=id)

def redirect_read(id):
    #redirect randomly if no_preview not provided
    try:
        pkg_dict = toolkit.get_action(
            'package_show')({}, {'id':id})
    except (NotFound):
        return dataset.read('dataset',id)

    redirect_without_no_preview = random.randrange(2)
    if (pkg_dict.get('nominated_view_id') not in ['',None]):
        preview = request.args.get('no_preview')
        if preview or redirect_without_no_preview:
            return dataset.read('dataset',id)
        else:
            return toolkit.h.redirect_to(f'/dataset/{id}?no_preview=0')
    else:
        return dataset.read('dataset',id)


vic_odp.add_url_rule( u'/dataset/groups/<id>', view_func=vic_groups_list)
