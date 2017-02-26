# -------------------------------------------------------------------------
# Footy definitions
# -------------------------------------------------------------------------


db.define_table('referees',
                Field('name'),
                format='%(name)s')

db.define_table('locations',
                Field('name', 'string'),
                format='%(name)s')

db.define_table('competitions',
                Field('name', 'string'),
                Field('location_id', 'reference locations'),
                format='%(name)s')

db.define_table('matches',
                Field('title', 'string'),
                Field('datetime', 'datetime'),
                Field('home_team', 'reference teams'),
                Field('home_goals', 'integer'),
                Field('visiting_team', 'reference teams'),
                Field('visiting_goals', 'integer'),
                Field('score', 'string'),
                Field('referee_id', 'reference referees'),
                Field('motm', 'reference auth_user'),
                Field('motm_fallback', 'string'),
                Field('division_id', 'reference divisions'),
                Field('location_id', 'reference locations'),
                Field('competition_id', 'reference competitions'),
                format='%(home_team)s %(visiting_team)s')

db.define_table('competition_has_division',
                Field('competition_id', 'reference competitions'),
                Field('division_id', 'reference divisions'),
                format='%(competition_id)s')

db.define_table('location_has_competitions',
                Field('location_id', 'reference locations'),
                Field('competition_id', 'reference competitions'),
                format='%(competition_id)s')

db.define_table('player_has_team',
                Field('team_id', 'reference teams'),
                Field('player_id', 'reference auth_user'),
                Field('start_date', 'datetime'),
                Field('end_date', 'datetime'),
                format='%(team_id)s')

db.define_table('goals',
                Field('number_of_goals', 'integer'),
                Field('match_id', 'reference matches'),
                Field('player_id', 'reference auth_user'),
                format='%(number_of_goals)s')

db.define_table('player_has_cards',
                Field('yellow_cards', 'integer'),
                Field('red_cards', 'boolean'),
                Field('player_id', 'reference auth_user'),
                Field('match_id', 'reference matches'))

db.define_table('att_options',
                Field('joining', requires=IS_IN_SET(['Yes', 'No', 'Maybe'])),
                format='%(joining)s')

db.define_table('attendance',
                Field('match_id', 'reference matches'),
                Field('joining_option', 'reference att_options'),
                Field('player_id', 'reference auth_user'),
                format='%(joining_option)s')



db.executesql('CREATE UNIQUE INDEX IF NOT EXISTS i_teams ON teams (name);')
db.executesql('CREATE UNIQUE INDEX IF NOT EXISTS i_divisions ON divisions (name);')
db.executesql('CREATE UNIQUE INDEX IF NOT EXISTS i_locations ON locations (name);')
db.executesql('CREATE INDEX IF NOT EXISTS i_matches ON matches (title, home_team, visiting_team);')

