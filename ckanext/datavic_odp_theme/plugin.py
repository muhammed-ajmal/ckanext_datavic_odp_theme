import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.datavic_odp_theme import helpers


class DatavicODPTheme(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'datavic_odp_theme')

    # ITemplateHelpers

    def get_helpers(self):
        ''' Return a dict of named helper functions (as defined in the ITemplateHelpers interface).
        These helpers will be available under the 'h' thread-local global object.
        '''
        return {
            'organization_list': helpers.organization_list,
            'group_list': helpers.group_list,
            'format_list': helpers.format_list,
            'hotjar_tracking_enabled': helpers.hotjar_tracking_enabled,
            'monsido_tracking_enabled': helpers.monsido_tracking_enabled,
            'get_hotjar_hsid': helpers.get_hotjar_hsid,
            'get_hotjar_hjsv': helpers.get_hotjar_hjsv,
            'get_monsido_domain_token': helpers.get_monsido_domain_token,
            'get_ga_tracking_id': helpers.get_ga_tracking_id,
            'get_ga_site': helpers.get_ga_site,
        }
