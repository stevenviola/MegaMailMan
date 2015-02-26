"""

Reads config.yaml for config values
Sets the config values as attributes to this function

To get a config value from another module, do:

import config
value = config.key

"""

import yaml
import sys
import logging

thismodule = sys.modules[__name__]
enabled_services = []
with open("config.yaml", 'r') as ymlfile:
    for key,value in yaml.load(ymlfile).iteritems():
        enabled_services.append(key)
        setattr(thismodule, key, value)
        logging.info("Enabling the service %s" % key)
    setattr(thismodule, 'enabled_services', enabled_services)