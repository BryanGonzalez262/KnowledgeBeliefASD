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
        title = "Welcome"
        stim = ["In this study, we'd like you to make judgments about whether certain statements are true or false.",
                "To indicate that something is false, you'll press the <b>[f]</b> key.",
                "To indicate that something is true, please press the <b>[j]</b> key.",
                'To get you used to this, you will first go through a warm-up phase. <br> On these trials, press <b>f</b> if you see the word "False" <br> and press <b>j</b> if you see the word "True."']
        next = "/tf_practice"
        return render_template('instruct.html', title=title, stim=stim, next=next)
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

        return make_response("200")

@app.route('/fixation', methods=['GET', 'POST'])
def fixation():
    if request.method == 'GET':
        return render_template('fixation.html')


@app.route('/task_instruct', methods=["GET", "POST"])
def task_instruct():
    title = "Task Instructions"
    next = "/story"
    stim = ["In this part of the study, you will be shown 24 short stories about different people and then you will have to answer a question about the story you read.",
            "***Please pay very close attention and answer as quickly and accurately as you possibly can. If you don't respond within 5 seconds, we will go to the next question.***",
            "Before starting there will be two practice examples of the sort of task you'll be doing. Remember, you'll have to read and respond quickly."]
    return render_template('instruct.html', title=title, stim=stim, next=next)


@app.route('/next_trial', methods = ['GET'])
def next_trial():
    t = int(request.args.get('trial'))+1
    if request.args.get('exp_state') == "TF_TRIAL":
        if t <= n_trials:
            return redirect(url_for('ready', PROLIFIC_PID=request.args.get('PROLIFIC_PID'),
                                    SESSION_ID=request.args.get('SESSION_ID'), exp_state="TF_TRIAL", trial=t))
        else:
            subj =Subject.query.filter_by(prolific_id=request.args.get('PROLIFIC_PID')).first()
            subj.block1_complete = True
            db.session.add(subj)
            db.session.commit()
            return redirect(url_for('ready', PROLIFIC_PID=request.args.get('PROLIFIC_PID'),
                                    SESSION_ID=request.args.get('SESSION_ID'), exp_state="FELICITY_PRACTICE", trial=1))

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



msgs = {e_state: {var: None for var in [1, 2, 'next']} for e_state in ['TRIAL_PRACTICE', 'TF_TRIAL', 'FELICITY_PRACTICE']}

msgs["TRIAL_PRACTICE"][1] = "Okay, one more practice example"
msgs["TRIAL_PRACTICE"][2] = "Press the space bar to continue, then place your fingers on the [f] and [j] keys.... "
msgs["TRIAL_PRACTICE"]['next'] = "/story"
msgs["TF_TRIAL"][1] = "Okay, get ready for the next story." #"Okay, get ready for story #" + request.args.get('trial') + "."
msgs["TF_TRIAL"][2] = "Press the space bar to continue, then place your fingers on the [f] and [j] keys.... "
msgs["TF_TRIAL"]['next'] = "/story"
msgs["FELICITY_PRACTICE"][1] = "Great Job!"
msgs["FELICITY_PRACTICE"][2] = "Press the space bar to continue.... "
msgs["FELICITY_PRACTICE"]['next'] = "/felicity_instr"



@app.route('/ready', methods=['GET', 'POST'])
def ready():

    return render_template('message.html', msg1=msgs[request.args.get('exp_state')][1],
                           msg2=msgs[request.args.get('exp_state')][2],
                           next=msgs[request.args.get('exp_state')]['next'])


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

@app.route('/felicity_instr')
def felicity_instr():
    title = "Great Job! Phase 2 Instructions"
    stim = ["In the next part of the experiment you will be asked to judge whether things that people say sound weird or normal.",
            "Here's an example of what we mean.<br>Suppose that your friend has three apples in front of him and after looking at them, he says, \"I have an apple in front of me.\"  <br>That's a weird thing to say.  It's true that there is a apple in front of him, but it sounds weird because there's not just one apple, there are actually three.  <br>A more normal thing to say would be \"I have three apples in front of me.\"",
            "Here's another example.<br> Suppose that Mary got married and then had a baby two years later. Somebody then says, \"My friend Mary had a baby and got married.\"<br> Again, this is technically true because she did do both of those things.  But, it sounds weird because it seems to imply that she had the baby first and got married second, but she actually got married first and had the baby later. <br> A more normal thing to say would be \"Mary got married and had a baby.\"",
            "Here's one last example.<br> Suppose Bruce accidentally hit his friend's hand with a hammer during a construction project.  Later somebody describes what happens by saying, \"Bruce broke a finger.\" <br> Again, this might be considered weird to say, because it seems to imply that Bruce broke his own finger, but he actually broke someone else's finger.  However, despite sounding weird, this sentence is technically true.",
            "In this part of the experiment you will read a number of stories, and after each story we will give you a statement that somebody made about the story.  <br>Your job is to judge whether the statement sounds weird or normal.",
            "Please try to remember that whether or not a sentence is true or false is a completely separate question from whether or not the sentence sounds normal or weird. <br>Some true sentences can sound weird, and some false sentences can sound normal.<br> Before starting, we want to make sure you understood the instructions by giving you some example questions."]
    next="/story"
    return render_template('instruct.html', title=title, stim=stim, next=next)

if __name__ == '__main__':
    app.run()
