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


# DATABASE CONFIGURATION
# Check whether POSTGRES_ENABLED env var is set to True or not.
# If so, generate connection string.
if app_config.has_key('postgres'):
    db_log = "{}/databases/sql.log".format(request.folder)
    open(db_log, 'w')
    settings.db_uri = 'postgres://{u}:{p}@{h}:{po}/{db}'.format(
        u=app_config.get('postgres.username'),
        p=app_config.get('postgres.password'),
        h=app_config.get('postgres.hostname'),
        po=app_config.get('postgres.port'),
        db=app_config.get('postgres.database'))
else:
    settings.db_uri = app_config.get('db.uri')
