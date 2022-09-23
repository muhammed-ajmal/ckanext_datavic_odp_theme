from requests import utils

import ckan.plugins.toolkit as tk

DEFAULT_AGENT = utils.default_user_agent()
CONFIG_AGENT = "ckanext.datavic.odp.user_agent"

# Immitate browser's User-Agent because firewall blocks requests from
# background jobs with the default User-Agent
utils.default_user_agent = lambda *a, **k: tk.config.get(CONFIG_AGENT, DEFAULT_AGENT)
