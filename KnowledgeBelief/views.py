from . import app, db
from .models import Subject, Trial, Felicity, Practice
from .utils import randomize_trials
import numpy as np
import pandas as pd
import random
import json
from flask import redirect, url_for, render_template, request, make_response
from datetime import datetime
from ast import literal_eval


json_fp = 'KnowledgeBelief/static/stim_data/KB_stim.json'
with open(json_fp, 'r') as j:
    stim = json.loads(j.read())

n_trials = 2


@app.route('/')
def index():
    # replace random with comments on prolific
    prolific_id = np.random.random()  # request.args.get('PROLIFIC_PID')
    session_id = np.random.random()  # request.args.get('SESSION_ID')

    return redirect(url_for('welcome', PROLIFIC_PID=prolific_id, SESSION_ID=session_id,
                            tf_practice='NotDone', trial_practice='NotDone', trial=0))


@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    msg1 = "Welcome!"
    msg2 = "Press the space bar to continue..."
    next = "/consent"
    return render_template('message.html', msg1=msg1, msg2=msg2, next=next)


@app.route('/consent', methods=['GET', 'POST'])
def consent():
    if request.method == 'GET':
        return render_template('consent.html')
    if request.method == 'POST':
        return make_response("200")


@app.route('/new_subject')
def new_subject():
    s_prac, s_trls, s_fel = randomize_trials()
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
                   block1_complete=False,
                   block2_complete=False)
    db.session.add(subj)


    for i, trl in s_trls.iterrows():
        db.session.add(Trial(trial_num=trl.trial_num, trial_type=trl.trial_type, scenario=trl.scenario,
                             belief_type=trl.belief, ascription_type=trl.ascription, correct_answer=trl.crrct_answer,
                             prolific_id=subj.prolific_id))

        if i <=11:
            db.session.add(Felicity(block2_trial_num=int(s_fel.b2_trial_num[i]),
                                    block1_trial_num=int(s_fel.b1_trial_num[i]),
                                    fel_scenario=int(s_fel.fel_scenario[i]), fel_belief_type=s_fel.fel_belief_type[i],
                                    fel_ascription_type=s_fel.fel_ascription_type[i], prolific_id=subj.prolific_id))
            if i <= 9:
                db.session.add(Practice(trial_num=int(s_prac.trial_num[i]), trial_type=s_prac.trial_type[i],
                                        prompt=str(s_prac.prompt[i]), target=s_prac.target[i],
                                        correct_answer=s_prac.correct_answer[i], prolific_id=subj.prolific_id))


    db.session.commit()
    return redirect(url_for('instructions',
                            PROLIFIC_PID=request.args.get('PROLIFIC_PID'), SESSION_ID=request.args.get('SESSION_ID'),
                            exp_state="TF_PRACTICE", trial=1))


@app.route('/instructions', methods=['GET', 'POST'])
def instructions():
    if request.method == 'GET':
        return render_template('instructions.html')
    else:
        return make_response("200")


@app.route('/tf_practice', methods=['GET', 'POST'])
def tf_practice():
    if request.method == 'GET':
        if int(request.args.get('trial')) <= 8:
            tdat = Practice.query.filter_by(prolific_id=request.args.get('PROLIFIC_PID'),
                                            trial_num=int(request.args.get('trial'))).first()
            return render_template('TF_practice.html', prompt=tdat.prompt, trl=tdat.trial_num)
        else:
            return redirect(url_for('task_instruct',
                                    PROLIFIC_PID=request.args.get('PROLIFIC_PID'),
                                    SESSION_ID=request.args.get('SESSION_ID'),
                                    exp_state='TRIAL_PRACTICE', trial=request.args.get('trial')))

    if request.method == 'POST':
        sub_dat = request.get_json()
        tdat = Practice.query.filter_by(prolific_id=sub_dat['PROLIFIC_PID'], trial_type='tf_practice',
                                        trial_num=int(sub_dat['trl'])).first()
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


@app.route('/next_trial', methods = ['GET'])
def next_trial():
    t = int(request.args.get('trial'))+1
    if request.args.get('exp_state') == "TF_TRIAL":
        return redirect(url_for('ready', PROLIFIC_PID=request.args.get('PROLIFIC_PID'),
                         SESSION_ID=request.args.get('SESSION_ID'), exp_state="TF_TRIAL", trial=t))

    elif request.args.get('exp_state') == "TF_PRACTICE":
        return redirect(url_for('tf_practice', PROLIFIC_PID=request.args.get('PROLIFIC_PID'), SESSION_ID=request.args.get('SESSION_ID'),
                                exp_state='TF_PRACTICE', trial=t))

    elif request.args.get('exp_state') == "TRIAL_PRACTICE":
        if t == 11:
            state = "TF_TRIAL"
            trl = 1
        else:
            state = "TRIAL_PRACTICE"
            trl = t
        return redirect(url_for('ready', PROLIFIC_PID=request.args.get('PROLIFIC_PID'),
                                SESSION_ID=request.args.get('SESSION_ID'), exp_state=state, trial=trl))


@app.route('/ready', methods=['GET', 'POST'])
def ready():
    if request.args.get('exp_state') != "TRIAL_PRACTICE":
        msg1 = "Okay, get ready for story #"+ request.args.get('trial')+"."
    else:
        msg1 = "Okay, one more practice example"
    msg2 = "Press the space bar to continue, then place your fingers on the [f] and [j] keys.... "
    return render_template('message.html', msg1=msg1, msg2=msg2, next="/story")


@app.route('/story', methods=['GET', 'POST'])
def story():
    if request.method == 'GET':
        if request.args.get('exp_state') != "TRIAL_PRACTICE":
            tdat = Trial.query.filter_by(prolific_id=request.args.get('PROLIFIC_PID'),
                                            trial_num=int(request.args.get('trial'))).first()
            story = stim[tdat.trial_type][str(tdat.scenario)]['belief_manip'][tdat.belief_type]
            ascrip = stim[tdat.trial_type][str(tdat.scenario)]['ascription'][tdat.ascription_type]

            return render_template('story.html', s1=story[0], s2=story[1], s3=story[2], s4=story[3],
                                   target=ascrip['target'], correct=ascrip['crrct_answr'],
                                   trl=int(request.args.get('trial')), ttype=tdat.trial_type)
        else: # Practice
            if int(request.args.get("trial")) <= 10:
                tdat = Practice.query.filter_by(prolific_id=request.args.get('PROLIFIC_PID'),
                                                trial_num=int(request.args.get('trial'))).first()
                story = literal_eval(tdat.prompt)
                return render_template('story.html', s1=story[0], s2=story[1], s3=story[2], s4=story[3], target=tdat.target,
                                       correct=tdat.correct_answer, trl=tdat.trial_num, ttype=tdat.trial_type)
            else:
                return redirect(url_for('ready',PROLIFIC_PID=request.args.get('PROLIFIC_PID'),
                                        SESSION_ID=request.args.get('SESSION_ID'), exp_state="TF_TRIAL", trial=1))

    if request.method == 'POST':
        sub_dat = request.get_json()
        if sub_dat['trl_type'] != 'story_practice':
            tdat = Trial.query.filter_by(prolific_id=sub_dat['PROLIFIC_PID'],
                                         trial_num=int(sub_dat['trl'])).first()
            tdat.correct = [True if sub_dat['keys_pressed'][-1] == tdat.correct_answer else False][0]

        else:
            tdat = Practice.query.filter_by(prolific_id=sub_dat['PROLIFIC_PID'],
                                            trial_num=int(sub_dat['trl'])).first()
            tdat.correct = True

        tdat.target_onset = datetime.fromtimestamp(sub_dat['target_onset'] / 1000.0)
        tdat.response_key = str(sub_dat['keys_pressed'])
        tdat.response_onset = datetime.fromtimestamp(sub_dat['rt'][-1] / 1000.0)
        db.session.add(tdat)
        db.session.commit()

        return make_response("200")




if __name__ == '__main__':
    app.run()
