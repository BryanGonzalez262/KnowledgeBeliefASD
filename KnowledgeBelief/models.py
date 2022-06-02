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
    block1_complete = db.Column(db.Boolean)
    block2_complete = db.Column(db.Boolean)
    completion_code = db.Column(db.VARCHAR(80))
    trials = db.relationship('Trial', backref='subject', lazy='dynamic', cascade="all, delete-orphan")
    felicity = db.relationship('Felicity', backref='subject', lazy='dynamic', cascade="all, delete-orphan")
    demographics = db.relationship('Demographic', backref='subject', lazy='dynamic', cascade="all, delete-orphan")



class Demographic(db.Model):
    __tablename__ = 'demographics'
    id = db.Column(db.Integer, primary_key=True)
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
    prolific_id = db.Column(db.String, db.ForeignKey('subjects.prolific_id'))


class AutismScore(db.Model):
    __tablename__ = 'autism_scores'
    id = db.Column(db.Integer, primary_key=True)



class Trial(db.Model):
    __tablename__ = 'trials'
    id = db.Column(db.Integer, primary_key=True)
    trial_num = db.Column(db.Integer, unique=False, index=True)
    prompt = db.Column(db.VARCHAR(400))
    correct = db.Column(db.Boolean)
    trial_type = db.Column(db.VARCHAR(10))
    scenario = db.Column(db.Integer)
    belief_type = db.Column(db.VARCHAR(3))  # True Belief (TB), False Belief (FB), No Belief/ignorance (IG)
    ascription_type = db.Column(db.VARCHAR(10))  # "knows" or "thinks"
    target = db.Column(db.VARCHAR(400))
    correct_answer = db.Column(db.VARCHAR(2))
    target_onset = db.Column(db.DateTime)
    response_onset = db.Column(db.DateTime)
    response_key = db.Column(db.VARCHAR(20))
    prolific_id = db.Column(db.String, db.ForeignKey('subjects.prolific_id'))


class Felicity(db.Model):
    __tablename__ = 'felicities'
    id = db.Column(db.Integer, primary_key=True)
    block1_trial_num = db.Column(db.Integer)
    block2_trial_num = db.Column(db.Integer)
    fel_scenario = db.Column(db.Integer)
    fel_belief_type = db.Column(db.VARCHAR(3))
    fel_ascription_type = db.Column(db.VARCHAR(10))  # "knows" or "thinks"
    fel_target = db.Column(db.VARCHAR(400))
    felicity_rating = db.Column(db.Integer)
    prolific_id = db.Column(db.String, db.ForeignKey('subjects.prolific_id'))

