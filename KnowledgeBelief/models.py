from . import db


class Subject(db.Model):
    __tablename__ = 'subjects'
    prolific_id = db.Column(db.String(64), unique=True, primary_key=True, index=True)
    session_id = db.Column(db.VARCHAR(300))
    participation_date = db.Column(db.DateTime)
    browser = db.Column(db.VARCHAR(80))
    browser_version = db.Column(db.VARCHAR(80))
    screen_width = db.Column(db.Integer)
    screen_height = db.Column(db.Integer)
    operating_sys = db.Column(db.VARCHAR(80))
    operating_sys_lang = db.Column(db.VARCHAR(80))
    GMT_timestamp = db.Column(db.DateTime)
    local_timestamp = db.Column(db.DateTime)
    completion = db.Column(db.Boolean)
    completion_code = db.Column(db.VARCHAR(80))


class Demographic(db.Model):
    __tablename__ = 'demographics'
    age = db.Column(db.Integer)
    sex = db.Column(db.VARCHAR(20))
    ethnicity = db.Column(db.VARCHAR(80))
    education = db.Column(db.VARCHAR(80))
    occupation = db.Column(db.VARCHAR(80))
    country = db.Column(db.VARCHAR(80))
    childhood_country = db.Column(db.VARCHAR(80))
    affiliated_country = db.Column(db.VARCHAR(80))
    language = db.Column(db.VARCHAR(80))
    n_siblings = db.Column(db.Integer)
    married = db.Column(db.Boolean)
    n_children = db.Column(db.Integer)


class AutismScore(db.Model):
    __tablename__ = 'autism_scores'


class Trial(db.Model):
    __tablename__ = 'trials'
    trial_num = db.Column(db.Integer)
    belief_type = db.Column(db.VARCHAR(2))  # True Belief (TB), False Belief (FB), No Belief/ignorance (IG)
    ascription_factive = db.Column(db.Boolean)  # "knows" or "thinks"
    distractor = db.Column(db.Boolean)
    scenario = db.Column(db.Integer)
    target = db.Column(db.VARCHAR(400))
    target_onset = db.Column(db.DateTime)
    response_onset = db.Column(db.DateTime)
    response_key = db.Column(db.VARCHAR(1))
    sound_weird = db.Column(db.Integer)
    sound_normal = db.Column(db.Integer)
