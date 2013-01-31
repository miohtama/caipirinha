"""

    Shared configuration and other facilities between bot instances and web server instance.

"""

import mongoengine


def get_public_url(settings):
    """
    Get public URL address our bot advertises.
    """
    return settings["caipirinha.public_url"]


def get_database_connection(settings):
    """
    """
    db_uri = settings['mongodb.url']
    conn = mongoengine.connect(db_uri)
    return conn


def get_database(conn, settings):
    """
    """
    db_name = settings['mongodb.db_name']
    return conn[db_name]
