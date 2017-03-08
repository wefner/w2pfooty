import json
import logging
import logging.config
from footylib import Footy
from gluon.scheduler import Scheduler


SCHEDULER = Scheduler(db)


def update_db_from_footy(config):
    try:
        logging_config = json.loads(open(config['logging_config']).read())
        logging.config.dictConfig(logging_config)
        logger = logging.getLogger('update_db_from_footy')
    except Exception as e:
        raise Exception('Exception while initializing logging. '
                        'Exception type: {t}. Error is: '
                        '{e}'.format(t=str(type(e)), e=str(e)))
    logger.info('Updating Competitions, Teams and Matches ')

    create_att_options()
    footy = Footy()
    competitions = footy.competitions
    for competition in competitions:
        location = db.locations.update_or_insert(name=competition.location)
        if not location:
            location = db(db.locations.name == competition.location).select().first().id

        competition_name = db.competitions.update_or_insert(
            name=competition.name,
            location_id=location)
        if not competition_name:
            competition_name = db((db.competitions.name == competition.name) &
                                  (db.competitions.location_id == location)).select().first().id
        db.location_has_competitions.update_or_insert(location_id=location,
                                                      competition_id=competition_name)
        for team in competition.teams:
            team_division = team.division
            if not team_division:
                team_division = 'unknown'
            division_name = db.divisions.update_or_insert(name=team_division)

            if not division_name:
                division_name = db(
                    db.divisions.name == team_division).select(
                                                        cache=(cache.ram,3600),
                                                        cacheable=True).first().id
            db.competition_has_division.update_or_insert(
                competition_id=competition_name,
                division_id=division_name)

            where = (db.teams.name == team.name)
            db.teams.update_or_insert(where,
                                      name=team.name,
                                      division_id=division_name)
        for match in competition.matches:
            division = db(db.divisions.name == match.division).select().first().id
            home_team = db(db.teams.name == match.home_team.name).select().first().id
            visiting_team = db(db.teams.name == match.visiting_team.name).select().first().id

            referee = db.referees.update_or_insert(name=match.referee)
            if not referee:
                referee = db(db.referees.name == match.referee).select(cache=(cache.ram,3600),
                                                                       cacheable=True).first().id
            db_match = db.matches.update_or_insert(title=match.title)
            if not db_match:
                db_match = db(db.matches.title == match.title).select(cache=(cache.ram,3600),
                                                                      cacheable=True).first().id
            where = (db.matches.id == db_match)
            db.matches.update_or_insert(where,
                                        motm=get_motm(match.motm),
                                        referee_id=referee,
                                        division_id=division,
                                        datetime=match.datetime,
                                        home_goals=normalize_goals(match.home_team_goals),
                                        location_id=location,
                                        competition_id=competition_name,
                                        home_team=home_team,
                                        motm_fallback=match.motm,
                                        visiting_goals=normalize_goals(match.visiting_team_goals),
                                        visiting_team=visiting_team,
                                        score=match.score)
    db.commit()


def update_standings(config):
    try:
        logging_config = json.loads(open(config['logging_config']).read())
        logging.config.dictConfig(logging_config)
        logger = logging.getLogger('update_standings')
    except Exception as e:
        raise Exception('Exception while initializing logging. '
                        'Exception type: {t}. Error is: '
                        '{e}'.format(t=str(type(e)), e=str(e)))
    logger.info('Updating Standings')

    footy = Footy()
    competitions = footy.competitions
    for competition in competitions:
        for team in competition.teams:
            try:
                division_id = db(
                    db.divisions.name == team.division).select().first().id
            except AttributeError:
                msg = "No division for team {}".format(team.name)
                logger.exception(msg)
            team_id = db(
                db.teams.name == team.name).select().first().id

            where_standing = db.standings.update_or_insert(team_id=team_id, division_id=division_id)
            if not where_standing:
                where_standing = db(
                    (db.standings.division_id == division_id) &
                    (db.standings.team_id == team_id)).select().first().id
            db.standings.update_or_insert(where_standing,
                                          pos=team.position,
                                          played_games=team.played_games,
                                          won_games=team.won_games,
                                          lost_games=team.lost_games,
                                          tie_games=team.tie_games,
                                          goals=team.goals,
                                          calendar=team.calendar.to_ical(),
                                          diff=team.diff,
                                          points=team.points,
                                          team_id=team_id,
                                          division_id=division_id)
    db.commit()


def get_motm(name):
    motm = None
    where_motm = db((db.auth_user.last_name == name) |
                    (db.auth_user.first_name == name)).select().first()
    if where_motm:
        motm = where_motm.id
    return motm


def create_att_options():
    options = ['Yes', 'No', 'Maybe']
    for option in options:
        db.att_options.update_or_insert(joining=option)


def normalize_goals(goals):
    return goals if goals != '-' else None


if not db((db.scheduler_task.task_name == 'update_db_from_footy')).select():
    SCHEDULER.queue_task(update_db_from_footy,
                         pvars={
                            'config': {
                                'logging_config':
                                    settings.logging_config['scheduler']}},
                         timeout=600,
                         period=3600,
                         repeats=0,
                         retry_failed=3)


if not db((db.scheduler_task.task_name == 'update_standings')).select():
    SCHEDULER.queue_task(update_standings,
                         pvars={
                             'config': {
                                 'logging_config':
                                     settings.logging_config['scheduler']}},
                         timeout=600,
                         period=3600,
                         repeats=0,
                         retry_failed=3)
