# ckanext-datavic-odp-theme
A custom CKAN extension theme for Data.vic.gov.au (Public)

## Installation

Activate the Python virtual environment:

        . /usr/lib/ckan/default/bin/activate

Install the CKAN extension:

        cd /usr/lib/ckan/default/src/ckanext-datavic-odp-theme

        python setup.py develop
        
*Add* `datavic_odp_theme` to plugins in /etc/ckan/default/development.ini & /etc/ckan/default/production.ini

        ckan.plugins = [...existing plugins...] datavic_odp_theme

Restart CKAN

        paster serve /etc/ckan/default/development.ini

Or... Restart Nginx & Apache:

        sudo service nginx stop
        sudo service apache2 stop
        sudo service apache2 start
        sudo service nginx start
