"""

    Shared configuration and other facilities between bot instances and web server instance.

"""

import pymongo


def get_database(settings):
    """
    """
    db_uri = settings['mongodb.url']
    db_name = settings['mongodb.db_name']
    db = settings['mongodb_conn'][db_name]

    MongoDB = pymongo.Connection

    if 'pyramid_debugtoolbar' in set(settings.values()):
        class MongoDB(pymongo.Connection):
            def __html__(self):
                return 'MongoDB: <b>{}></b>'.format(self)

    conn = MongoDB(db_uri)

    return conn, db

