from . import app, db
from .models import Subject, Trial, Demographic, AutismScore
from .utils import randomize_trials
import numpy as np
import pandas as pd
import random
import json
from flask import redirect, url_for, render_template, request, make_response
from datetime import datetime


@app.route('/')
def index():  # put application's code here
    # on remote set these
    # prolific_id = request.args.get('PROLIFIC_PID'),
    # flask_subId = request.args.get('flasker')

    return redirect(url_for('welcome', PROLIFIC_PID=np.random.random(),
                            SESSION_ID=np.random.random(), trial=0))


@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    return render_template('welcome.html')


@app.route('/consent', methods=['GET', 'POST'])
def consent():
    if request.method == 'GET':
        return render_template('consent.html')
    if request.method == 'POST':
        return make_response("200")


@app.route('/new_subject')
def new_subject():
    sub_trls = randomize_trials()
    print('You have a new Subject')
    ua = request.user_agent
    subj = Subject(prolific_id=request.args.get('PROLIFIC_PID'),
                   session_id=request.args.get('SESSION_ID'),
                   participation_date=datetime.now(),
                   browser=ua.browser,
                   browser_version=ua.version,
                   operating_sys=ua.platform,
                   operating_sys_lang=ua.language,
                   GMT_timestamp=datetime.utcnow(),
                   completion=False)
    db.session.add(subj)

    # Opening JSON file
    json_fp = 'KnowledgeBelief/static/stim_data/KB_stim.json'
    with open(json_fp, 'r') as j:
        stim = json.loads(j.read())
    for i, trl in sub_trls.iterrows():
        db.session.add(Trial(trial_num=trl.trial_num, prompt=str(trl.prompt), trial_type=trl.trial_type,
                        scenario=trl.scenario, belief_type=trl.belief, ascription_type=trl.ascription,
                        target=trl.target, correct_answer=trl.crrct_answer, prolific_id=subj.prolific_id))

    db.session.commit()
    return redirect(url_for('instructions', PROLIFIC_PID=request.args.get('PROLIFIC_PID'), SESSION_ID=request.args.get('SESSION_ID')))


@app.route('/instructions', methods=['GET', 'POST'])
def instructions():
    if request.method == 'GET':
        return render_template('instructions.html')
    else:
        return make_response("200")



@app.route('/tf_practice', methods=['GET', 'POST'])
def tf_practice():
    if request.method == 'GET':
        tdat = Trial.query.filter_by(prolific_id=request.args.get('PROLIFIC_PID'), trial_type='tf_practice', response_key=None).first()
        if tdat is not None:
            return render_template('TF_practice.html', prompt=tdat.prompt)
        else:
            return redirect(url_for('task_instruct', PROLIFIC_PID=request.args.get('PROLIFIC_PID'), SESSION_ID=request.args.get('SESSION_ID')))
    if request.method == 'POST':
        sub_dat = request.get_json()
        tdat = Trial.query.filter_by(prolific_id=sub_dat['PROLIFIC_PID'], trial_type='tf_practice', response_key=None).first()
        tdat.correct = True
        tdat.target_onset = datetime.fromtimestamp(sub_dat['target_onset']/1000.0)
        tdat.response_key = str(sub_dat['keys_pressed'])
        tdat.response_onset = datetime.fromtimestamp(sub_dat['rt'][-1]/1000.0)
        db.session.add(tdat)
        db.session.commit()

        return make_response("200") # redirect(url_for('fixation', PROLIFIC_PID=sub_dat['PROLIFIC_PID'], SESSION_ID=sub_dat['SESSION_ID']))


@app.route('/fixation', methods=['GET', 'POST'])
def fixation():
    if request.method == 'GET':
        return render_template('fixation.html')


@app.route('/task_instruct', methods=["GET", "POST"])
def task_instruct():
    return render_template('task_instruct.html')

if __name__ == '__main__':
    app.run()
