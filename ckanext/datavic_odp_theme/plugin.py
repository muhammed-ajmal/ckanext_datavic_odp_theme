import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.datavic_odp_theme.logic import auth_functions
from ckanext.datavic_odp_theme.views import get_blueprints
from ckanext.datavic_odp_theme.cli import get_commands
from ckanext.datavic_odp_theme.helpers import get_helpers


class DatavicODPTheme(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IMiddleware, inherit=True)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IClick)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("webassets", "datavic_odp_theme")

    # ITemplateHelpers
    def get_helpers(self):
        return get_helpers()

    # IMiddleware
    def make_middleware(self, app, config):
        return AuthMiddleware(app, config)

    # IAuthFunctions
    def get_auth_functions(self):
        return auth_functions()

    # IBlueprint
    def get_blueprint(self):
        return get_blueprints()

    # IClick
    def get_commands(self):
        return get_commands()


class AuthMiddleware(object):
    def __init__(self, app, app_conf):
        self.app = app

    def __call__(self, environ, start_response):
        # Redirect homepage (/) to /dataset
        if environ["PATH_INFO"] == "/":
            location = toolkit.h.url_for("dataset.search")
            headers = [("Location", location)]
            status = "301 Moved Permanently"
            start_response(status, headers)
            return []
        return self.app(environ, start_response)
