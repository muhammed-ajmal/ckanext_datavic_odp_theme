import ckan.plugins.toolkit as toolkit
import ckan.logic           as logic

from ckan.common import config, request

import ckan.model as model
import sqlalchemy

_and_ = sqlalchemy.and_
_func = sqlalchemy.func

def organization_list():
    return toolkit.get_action('organization_list')({}, {'all_fields': True})


def group_list():
    return toolkit.get_action('group_list')({}, {'all_fields': True})


def format_list(limit=100):
    session = model.Session

    query = (session.query(
        model.Resource.format,)
        .filter(_and_(
            model.Resource.state == 'active',
        ))
        .group_by(model.Resource.format)
        .order_by('format ASC'))

    return [resource.format for resource in query if not resource.format == '']
