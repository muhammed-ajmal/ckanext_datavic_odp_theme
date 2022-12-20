from flask import Blueprint

import ckan.lib.helpers as h
from ckan.common import request,config
import ckan.plugins.toolkit as toolkit
import ckan.views.dataset as dataset
import random


vic_odp = Blueprint('vic_odp', __name__)


def vic_groups_list(id):
    return h.redirect_to('dataset.read', id=id)

def redirect_read(id):
    #redirect randomly if no_preview not provided
    redirect_without_no_preview = random.randrange(2) 
    if config.get('ckan.dataset.preview_redirect', None):
        preview = request.args.get('no_preview')
        if preview or redirect_without_no_preview:
            return dataset.read('dataset',id)
        else:
            return toolkit.h.redirect_to(f'/dataset/{id}?no_preview=0')
    else:
        return dataset.read('dataset',id)

vic_odp.add_url_rule( u'/dataset/groups/<id>', view_func=vic_groups_list)
vic_odp.add_url_rule( u'/dataset/<id>', view_func=redirect_read)
