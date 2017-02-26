import tempfile
from datetime import datetime


@auth.requires_login()
def next_match():
    where_next_match = (((db.matches.visiting_team == auth.user.team_name) |
                         (db.matches.home_team == auth.user.team_name)) &
                         (db.matches.datetime > datetime.today()))
    match = db(where_next_match).select(db.matches.ALL,
                                        orderby=db.matches.datetime,
                                        cache=(cache.ram, 60),
                                        cacheable=True).first()
    where_attendance = (db.attendance.match_id == match.id)
    attendance = db(where_attendance).select(db.attendance.ALL)
    return dict(match=match, attendance=attendance)


def divisions():
    where = ((db.matches.division_id == request.args(0)))
             # (db.standings.team_id == db.teams.id) &
             # (db.standings.division_id == db.divisions.id))
    matches = db(where).select(db.matches.ALL,
                               distinct=True,
                               orderby=db.matches.division_id|db.matches.datetime)
    where_standing = (db.standings.division_id == request.args(0))
    standings = db(where_standing).select(db.standings.ALL)
    return dict(matches=matches, standings=standings)


def locations():
    where = ((db.matches.location_id == request.args(0)) &
             (db.divisions.id == db.matches.division_id) &
             (db.matches.location_id == db.locations.id))
    divisions = db(where).select(db.divisions.ALL, db.locations.name,
                                 distinct=True,
                                 orderby=db.divisions.name)
    location = divisions[0]['locations']['name']
    return dict(divisions=divisions, location=location)


@auth.requires_login()
def team_calendar():
    where = (db.standings.team_id == auth.user.team_name)
    standings = db(where).select(db.standings.ALL)
    tmp = tempfile.NamedTemporaryFile(prefix='calendar', suffix='.ics')
    for standing in standings.render():
        tmp.write(standing.calendar)
        tmp.flush()
    return response.stream(tmp.name, 512)
