# We need all this information in order to create the other tables.
# Standings provide the division ID so we need divisions table as well.
# We also need the teams in order for the user to select his/her
# team name when signing up.
# And then the auth_user table gets extended with team_name which
# is the ID of the team as a drop-down menu.



db.define_table('divisions',
                Field('name', 'string'),
                format='%(name)s')

db.define_table('teams',
                Field('name', 'string', unique=True),
                Field('division_id', 'reference divisions'),
                format='%(name)s')

db.define_table('standings',
                Field('points', 'integer'),
                Field('goals', 'integer'),
                Field('diff', 'integer'),
                Field('played_games', 'integer'),
                Field('won_games', 'integer'),
                Field('lost_games', 'integer'),
                Field('tie_games', 'integer'),
                Field('calendar', 'text'),
                Field('pos', 'integer'),
                Field('team_id', 'reference teams'),
                Field('division_id', 'reference divisions'))

db.define_table(auth.settings.table_user_name,
                Field('first_name', length=128, default=''),
                Field('last_name', length=128, default=''),
                Field('email', length=128, default='', unique=True),
                Field('password', 'password', length=512,
                      readable=False, label='Password',
                      comment="Must have a minimum length of 6"),
                Field('registration_key', length=512,
                      writable=False, readable=False, default=''),
                Field('reset_password_key', length=512, 
                      writable=False, readable=False, default=''),
                Field('registration_id', length=512,
                      writable=False, readable=False, default=''),
                Field('guest', 'boolean', writable=True, readable=True, default=0,
                      comment="Check this box if you don't have an official team"),
                Field('team_name', 'reference teams'),
                format='%(first_name)s')

custom = db[auth.settings.table_user_name]
custom.first_name.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)
custom.last_name.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)
custom.password.requires = [CRYPT()]
custom.email.requires = [
                IS_EMAIL(error_message=auth.messages.invalid_email),
                IS_NOT_IN_DB(db, custom.email)]

# -------------------------------------------------------------------------
# create all tables needed by auth if not custom tables
# -------------------------------------------------------------------------
auth.define_tables(username=False, signature=False)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.get('smtp.server')
mail.settings.sender = myconf.get('smtp.sender')
mail.settings.login = myconf.get('smtp.login')
mail.settings.tls = myconf.get('smtp.tls') or False
mail.settings.ssl = myconf.get('smtp.ssl') or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = True
auth.settings.registration_requires_approval = True
auth.settings.reset_password_requires_verification = True
auth.settings.password_min_length = 6

