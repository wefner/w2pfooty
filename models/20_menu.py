# -*- coding: utf-8 -*-

import logging

logger_basename = request.controller

# this file is released under public domain and you can use without limitations

# ----------------------------------------------------------------------------------------------------------------------
# Customize your APP title, subtitle and menus here
# ----------------------------------------------------------------------------------------------------------------------

response.title = request.application.replace('_', ' ').title()
response.subtitle = ''

# ----------------------------------------------------------------------------------------------------------------------
# read more at http://dev.w3.org/html5/markup/meta.name.html
# ----------------------------------------------------------------------------------------------------------------------
response.meta.author = myconf.get('app.author')
response.meta.description = myconf.get('app.description')
response.meta.keywords = myconf.get('app.keywords')
response.meta.generator = myconf.get('app.generator')

# ----------------------------------------------------------------------------------------------------------------------
# your http://google.com/analytics id
# ----------------------------------------------------------------------------------------------------------------------
response.google_analytics_id = None

# ----------------------------------------------------------------------------------------------------------------------
# this is the main application menu add/remove items as required
# ----------------------------------------------------------------------------------------------------------------------

response.menu = [
    (T('Home'), False, URL('default', 'index'), []),
    (T('Matches'), False, None, [
        (T('Download Season'), False, URL('matches', 'team_calendar')),
        (T('Your matches'), False, URL('default', 'index')),
         ])
    ]

LOCATIONS_MENU = True


def locations_menu():
    logger = logging.getLogger('{n}:'
                               '{f}'.format(n=logger_basename,
                                            f='locations_menu'))
    query = db().select(db.locations.ALL)
    menu_header = [T('locations'), False, None, []]
    for location in query:
        loc_submenu = []
        loc_submenu.append(T(location.name))
        loc_submenu.append(False)
        loc_submenu.append(URL('matches', 'locations', args=[location.id]))
        menu_header[-1].append(tuple(loc_submenu))
    logger.info('Locations created')
    return tuple(menu_header)


if LOCATIONS_MENU:
    response.menu += [locations_menu()]


if "auth" in locals():
    auth.wikimenu()
