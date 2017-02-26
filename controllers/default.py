# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------


@auth.requires_login()
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    where = (((db.player_has_team.team_id == auth.user.team_name) &
              (db.player_has_team.player_id == auth.user.id) &
              (
                  (db.matches.visiting_team == db.player_has_team.team_id) |
                  (db.matches.home_team == db.player_has_team.team_id)
              ) &
              (db.matches.division_id == db.divisions.id) &
              (db.divisions.id == db.standings.division_id)))
    matches = db(where).select(db.matches.ALL,
                               distinct=True,
                               orderby=db.matches.datetime,
                               )
    division_name = next((match for match in matches.render()), None).division_id.split(' ')[1:]
    division_link = A(' '.join(division_name), _href=URL('matches', 'divisions', args=matches[0].division_id))
    return dict(matches=matches, message=division_link)


@auth.requires_login()
def stats():
    where = ((auth.user.id == db.goals.player_id) &
             (db.goals.match_id == request.args(0)))
    stats_to_update = db(where).select().first()
    if stats_to_update:
        stats_to_update = stats_to_update.id
    else:
        stats_to_update = db.goals(request.args(0))

    form = SQLFORM(db.goals,
                   record=stats_to_update,
                   showid=False,
                   fields=['number_of_goals'])

    form.vars.player_id = auth.user.id
    form.vars.match_id = request.args(0)

    if form.process().accepted:
        response.flash = 'form accepted'
        redirect(URL('default', 'index'))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'
    return dict(form=form)


@auth.requires_login()
def attendance():
    where = ((auth.user.id == db.attendance.player_id) &
             (db.attendance.match_id == request.args(0)))
    match_to_update = db(where).select().first()
    if match_to_update:
        match_to_update = match_to_update.id
    else:
        match_to_update = db.attendance(request.args(0))

    form = SQLFORM(db.attendance,
                   record=match_to_update,
                   showid=False,
                   fields=['joining_option'],
                   )

    form.vars.joining_option = 3
    form.vars.player_id = auth.user.id
    form.vars.match_id = request.args(0)

    if form.process().accepted:
        response.flash = 'form accepted'
        redirect(URL('default', 'index'))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'
    return dict(form=form)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """

    # Create state as of when the user was joined in the team.
    if request.args(0) == 'verify_email':
        where = (db.auth_user.registration_key == request.args(1))
        player = db(where).select(db.auth_user.ALL).first()
        if player:
            db.player_has_team.insert(player_id=player.id,
                                      start_date=request.now,
                                      team_id=player.team_name)
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


