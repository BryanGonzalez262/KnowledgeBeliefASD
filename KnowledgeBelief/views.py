from . import app, db
from .models import Subject, Trial, Demographic, AutismScore
from .utils import randomize_trials
import numpy as np
import pandas as pd
import random
import json
from flask import redirect, url_for, render_template, request, make_response
from datetime import datetime
from ast import literal_eval


@app.route('/')
def index():  # put application's code here
    # on remote set these
    # prolific_id = request.args.get('PROLIFIC_PID'),
    # flask_subId = request.args.get('flasker')

    return redirect(url_for('welcome', PROLIFIC_PID=np.random.random(),
                            SESSION_ID=np.random.random(), trial=0))


@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    msg = "Welcome!"
    next = "/consent"
    return render_template('welcome.html', msg=msg, next=next)


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


    for i, trl in sub_trls.iterrows():
        db.session.add(Trial(trial_num=trl.trial_num, prompt=str(trl.prompt), trial_type=trl.trial_type,
                        scenario=trl.scenario, belief_type=trl.belief, ascription_type=trl.ascription,
                        target=trl.target, correct_answer=trl.crrct_answer, prolific_id=subj.prolific_id))

    db.session.commit()
    return redirect(url_for('instructions', PROLIFIC_PID=request.args.get('PROLIFIC_PID'),
                            SESSION_ID=request.args.get('SESSION_ID'), trial=0))


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
            return redirect(url_for('task_instruct', PROLIFIC_PID=request.args.get('PROLIFIC_PID'), SESSION_ID=request.args.get('SESSION_ID'), trial=0, tf_practice='Done'))
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
        if int(request.args.get('trial')) == 0:
            next = "/tf_practice"
            if request.args.get('tf_practice') == 'Done':
                next = "/story_practice"
        else:
            next = "/next_trial"
        return render_template('fixation.html', next=next)


@app.route('/task_instruct', methods=["GET", "POST"])
def task_instruct():
    return render_template('task_instruct.html')


@app.route('/next_trial')
def next_trial():
    if int(request.args.get('trial')) == 0:
        message = "Okay, one more practice example"
        render_template('welcome.html', msg=message, next="/story_practice")

    else:
        message = "Get ready for the next story.."
        return render_template('welcome.html', msg=message, next="/story")

            #redirect(url_for('invest', PROLIFIC_PID=request.args.get('PROLIFIC_PID'), SESSION_ID=request.args.get('SESSION_ID'),
            #                trial=int(int(request.args.get('trial')) + 1)))


# Opening JSON file
json_fp = 'KnowledgeBelief/static/stim_data/KB_stim.json'
with open(json_fp, 'r') as j:
    stim = json.loads(j.read())


@app.route('/story_practice', methods=['GET', 'POST'])
def story_practice():
    if request.method == 'GET':
        tdat = Trial.query.filter_by(prolific_id=request.args.get('PROLIFIC_PID'), trial_type='practice',
                                     response_key=None).first()
        if tdat is not None:
            story = literal_eval(tdat.prompt)
            return render_template('story.html', s1=story[0], s2=story[1], s3=story[2], s4=story[3], target=tdat.target,
                                   correct=tdat.correct_answer, trl=999)
        else:
            return redirect(url_for('next_trial', PROLIFIC_PID=request.args.get('PROLIFIC_PID'),
                                    SESSION_ID=request.args.get('SESSION_ID'),
                                    trial=int(int(request.args.get('trial')) + 1)))

    if request.method == 'POST':
        sub_dat = request.get_json()
        tdat = Trial.query.filter_by(prolific_id=sub_dat['PROLIFIC_PID'], trial_type='practice',
                                     response_key=None).first()
        tdat.correct = True
        tdat.target_onset = datetime.fromtimestamp(sub_dat['target_onset'] / 1000.0)
        tdat.response_key = str(sub_dat['keys_pressed'])
        tdat.response_onset = datetime.fromtimestamp(sub_dat['rt'][-1] / 1000.0)
        db.session.add(tdat)
        db.session.commit()

        return make_response("200")


@app.route('/story', methods=["GET", "POST"])
def story():
    if request.method == 'GET':
        tdat = Trial.query.filter_by(prolific_id=request.args.get('PROLIFIC_PID'), trial_num=int(request.args.get('trial')),
                                     response_key=None).first()

        if tdat is not None:
            story = stim[tdat.trial_type][str(tdat.scenario)]['belief_manip'][tdat.belief_type]
            ascrip = stim[tdat.trial_type][str(tdat.scenario)]['ascription'][tdat.ascription_type]

            return render_template('story.html', s1=story[0], s2=story[1], s3=story[2], s4=story[3],
                                   target=ascrip['target'],
                                   correct=ascrip['crrct_answr'], trl=int(request.args.get('trial')))
        else:
            return redirect(url_for('next_trial', PROLIFIC_PID=request.args.get('PROLIFIC_PID'),
                                    SESSION_ID=request.args.get('SESSION_ID'),
                                    trial=int(int(request.args.get('trial')) + 1)))

    if request.method == 'POST':
        sub_dat = request.get_json()
        tdat = Trial.query.filter_by(prolific_id=sub_dat['PROLIFIC_PID'], trial_num=sub_dat['trl'],
                                     response_key=None).first()
        tdat.correct = [True if literal_eval(sub_dat['keys_pressed'])[-1] == tdat.correct_answer else False]
        tdat.target_onset = datetime.fromtimestamp(sub_dat['target_onset'] / 1000.0)
        tdat.response_key = str(sub_dat['keys_pressed'])
        tdat.response_onset = datetime.fromtimestamp(sub_dat['rt'][-1] / 1000.0)
        db.session.add(tdat)
        db.session.commit()


        return "200"



if __name__ == '__main__':
    app.run()
