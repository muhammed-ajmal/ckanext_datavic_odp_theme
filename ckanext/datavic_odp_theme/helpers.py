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


def hotjar_tracking_enabled():
    return toolkit.asbool(config.get('ckan.tracking.hotjar_enabled', False))


def monsido_tracking_enabled():
    return toolkit.asbool(config.get('ckan.tracking.monsido_enabled', False))


def get_hotjar_hsid():
    return config.get('ckan.tracking.hotjar.hjid', None)


def get_hotjar_hjsv():
    return config.get('ckan.tracking.hotjar.hjsv', None)


def get_monsido_domain_token():
    return config.get('ckan.tracking.monsido.domain_token', None)


def get_ga_tracking_id():
    return config.get('googleanalytics.id', None)


def get_ga_site():
    from urlparse import urlparse
    site_url = config.get('ckan.site_url', None)
    o = urlparse(site_url)
    return o.hostname


def get_parent_site_url():
    return config.get('ckan.parent_site_url', 'https://www.data.vic.gov.au/')


def release_date(pkg_dict):
    """
    Copied from https://github.com/salsadigitalauorg/datavic_ckan_2.2/blob/develop/iar/src/ckanext-datavic/ckanext/datavic/plugin.py#L296
    :param pkg_dict:
    :return:
    """
    dates = []
    dates.append(pkg_dict['metadata_created'])
    for resource in pkg_dict['resources']:
        if 'release_date' in resource and resource['release_date'] != '' and resource['release_date'] != '1970-01-01':
            dates.append(resource['release_date'])
    dates.sort()
    return dates[0].split("T")[0]
