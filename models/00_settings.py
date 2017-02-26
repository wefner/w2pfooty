import os
import logging
import json
from logging.config import dictConfig
from gluon.storage import Storage
from gluon.contrib.appconfig import AppConfig


# app_config use to cache values in production
app_config = AppConfig(reload=True)

# settings is used to avoid cached values in production
settings = Storage()

# LOGGING CONFIGURATIONS
settings.logging_config = dict(main=os.path.join(request.folder,
                                                 'logging.json'),
                               scheduler=os.path.join(request.folder,
                                                      'logging-scheduler.json'))

# INITIALIZE LOGGING
if os.path.exists(settings.logging_config['main']):
    try:
        config = json.loads(open(settings.logging_config['main']).read())
        logging.config.dictConfig(config)
    except ValueError as e:
        pass

logger = logging.getLogger(settings.app_name)


