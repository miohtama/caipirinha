from pyramid.config import Configurator
#from pyramid.events import subscriber
from pyramid.events import NewRequest

from caipirinha.resources import Root
from caipirinha.shared import get_database


def main(global_config, **settings):
    """ This function returns a WSGI application.
    """
    config = Configurator(settings=settings, root_factory=Root)
    config.add_view('caipirinha.views.my_view',
                    context='caipirinha:resources.Root',
                    renderer='caipirinha:templates/mytemplate.pt')
    config.add_static_view('static', 'caipirinha:static')

    # MongoDB
    #
    def add_mongo_db(event):
        settings = event.request.registry.settings
        #url = settings['mongodb.url']
        db_name = settings['mongodb.db_name']
        db = settings['mongodb_conn'][db_name]
        event.request.db = db

    conn, db = get_database(settings)

    config.registry.settings['mongodb_conn'] = conn
    config.add_subscriber(add_mongo_db, NewRequest)
    config.scan('caipirinha')
    return config.make_wsgi_app()
