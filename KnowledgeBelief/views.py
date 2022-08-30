from . import app, db, recaptcha
from .models import Subject, Trial, Felicity, Practice, AutismScore, Demographic
from .utils import randomize_trials, fel_practice
import numpy as np
import json
from flask import redirect, url_for, render_template, request, make_response, current_app
from datetime import datetime
from ast import literal_eval
import random
import string
import requests
from urllib.request import urlopen
from json import load

json_fp = 'KnowledgeBelief/static/stim_data/KB_stim.json'
with open(json_fp, 'r') as j:
    stim = json.loads(j.read())

n_trials = 24
n_fel_trials = 12
comp_code = "XXXX"
cap_site_k = app.config["RECAPTCHA_SITE_KEY"]
cap_secret = app.config["RECAPTCHA_SECRET_KEY"]


@app.route('/')
def index():
    # replace random with comments on prolific
    prolific_id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
    session_id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))

    return redirect(url_for('welcome', PROLIFIC_PID=prolific_id, SESSION_ID=session_id,
                            tf_practice='NotDone', trial_practice='NotDone', trial=0))


@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    msg1 = "Welcome!"
    msg2 = "Press the space bar to continue..."
    next_pg = "/real"
    return render_template('message.html', msg1=msg1, msg2=msg2, next=next_pg)


@app.route('/real', methods=['GET', 'POST'])
def real():
    message = '' # Create empty message
    if request.method == 'POST': # Check to see if flask.request.method is POST
        r = requests.post('https://www.google.com/recaptcha/api/siteverify',
                          data={'secret': cap_secret,
                                'response': request.form['g-recaptcha-response']})

        google_response = json.loads(r.text)
        print('JSON: ', google_response)

        if google_response['success']:
            print('SUCCESS')
            message = 'Thanks for filling out the form!' # Send success message
        else:
            message = 'Please fill out the ReCaptcha!' # Send error message
        return render_template('real.html', msg1='Please verify', message=message, nxt="/consent", sk=cap_site_k)

    if request.method == 'GET':

        addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        url = 'https://ipinfo.io/' + addr + '/json'
        res = urlopen(url)
        # response from url(if res==None then check connection)
        data = load(res)
        print(data['country'])
        # check if english speaking country
        if data['country'] in ['GB', 'US', 'AG', 'AU', 'BS', 'BB', 'BZ', 'CA', 'DM' 'GD', 'GY', 'IE', 'JM', 'MT', 'NZ', 'KN', 'LC', 'VC', 'TT']:
            return render_template('real.html', msg1='Please verify', message=message, nxt="/consent", sk=cap_site_k)
        else:
            return render_template('message.html', msg1='Sorry',
                                   msg2='This is experiment is not available in your country. Please close this window now.', next="/real")


@app.route('/consent', methods=['GET', 'POST'])
def consent():
    if request.method == 'GET':
        return render_template('consent.html')
    if request.method == 'POST':
        return make_response("200")


@app.route('/new_subject')
def new_subject():
    prolific_id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
    session_id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))

    s_prac, s_trls, s_fel = randomize_trials()
    print('You have a new Subject')
    ua = request.user_agent
    subj = Subject(prolific_id=prolific_id,
                   session_id=session_id,
                   participation_date=datetime.now(),
                   browser=ua.browser,
                   browser_version=ua.version,
                   operating_sys=ua.platform,
                   operating_sys_lang=ua.language,
                   GMT_timestamp=datetime.utcnow(),
                   block1_complete=False,
                   block2_complete=False,
                   block3_complete=False)
    db.session.add(subj)
    # Add Trials
    for i, trl in s_trls.iterrows():
        db.session.add(Trial(trial_num=trl.trial_num, trial_type=trl.trial_type, scenario=trl.scenario,
                             belief_type=trl.belief, ascription_type=trl.ascription, correct_answer=trl.crrct_answer,
                             prolific_id=subj.prolific_id))

        if i <= 11:
            db.session.add(Felicity(block2_trial_num=int(s_fel.b2_trial_num[i]),
                                    block1_trial_num=int(s_fel.b1_trial_num[i]),
                                    fel_scenario=int(s_fel.fel_scenario[i]), fel_belief_type=s_fel.fel_belief_type[i],
                                    fel_ascription_type=s_fel.fel_ascription_type[i], prolific_id=subj.prolific_id))
            if i <= 9:
                db.session.add(Practice(trial_num=int(s_prac.trial_num[i]), trial_type=s_prac.trial_type[i],
                                        prompt=str(s_prac.prompt[i]), target=s_prac.target[i],
                                        correct_answer=s_prac.correct_answer[i], prolific_id=subj.prolific_id))
    # Add Autism & Demos Entry
    db.session.add(Demographic(prolific_id=prolific_id))
    db.session.add(AutismScore(prolific_id=prolific_id))
    db.session.commit()
    return redirect(url_for('instructions',
                            PROLIFIC_PID=prolific_id, SESSION_ID=session_id, tf_practice='NotDone', trial_practice='NotDone',
                            exp_state="TF_PRACTICE", trial=1))


@app.route('/instructions', methods=['GET', 'POST'])
def instructions():
    if request.method == 'GET':
        title = "Welcome"
        stym = ["In this study, we'd like you to make judgments about whether certain statements are true or false.",
                "To indicate that something is false, you'll press the <b>[f]</b> key.",
                "To indicate that something is true, please press the <b>[j]</b> key.",
                'To get you used to this, you will first go through a warm-up phase. <br> On these trials, press <b>f</b> if you see the word "False" <br> and press <b>j</b> if you see the word "True."',
                "Click Next to begin and then place your fingers on the [<b>f</b>] and [<b>j</b>] keys."]
        next_pg = "/tf_practice"
        return render_template('instruct.html', title=title, stim=stym, next=next_pg)
    else:
        return make_response("200")


@app.route('/tf_practice', methods=['GET', 'POST'])
def tf_practice():
    if request.method == 'GET':
        if int(request.args.get('trial')) <= 8:
            t_dat = Practice.query.filter_by(prolific_id=request.args.get('PROLIFIC_PID'),
                                             trial_num=int(request.args.get('trial'))).first()
            return render_template('TF_practice.html', prompt=t_dat.prompt, trl=t_dat.trial_num)
        else:
            return redirect(url_for('task_instruct',
                                    PROLIFIC_PID=request.args.get('PROLIFIC_PID'),
                                    SESSION_ID=request.args.get('SESSION_ID'),
                                    exp_state='TRIAL_PRACTICE', trial=request.args.get('trial')))

    if request.method == 'POST':
        sub_dat = request.get_json()
        t_dat = Practice.query.filter_by(prolific_id=sub_dat['PROLIFIC_PID'], trial_type='tf_practice',
                                         trial_num=int(sub_dat['trl'])).first()
        t_dat.correct = True
        t_dat.target_onset = datetime.fromtimestamp(sub_dat['target_onset']/1000.0)
        t_dat.response_key = str(sub_dat['keys_pressed'])
        t_dat.response_onset = datetime.fromtimestamp(sub_dat['rt'][-1]/1000.0)
        db.session.add(t_dat)
        db.session.commit()

        return make_response("200")


@app.route('/fixation', methods=['GET', 'POST'])
def fixation():
    if request.method == 'GET':
        return render_template('fixation.html')


@app.route('/task_instruct', methods=["GET", "POST"])
def task_instruct():
    title = "Task Instructions"
    next_page = "/story"
    stm = ["In this part of the study, you will be shown 24 short stories about different people and then you will have to answer a question about the story you read.",
           "***Please pay very close attention and answer as quickly and accurately as you possibly can. If you don't respond within 5 seconds, we will go to the next question.***",
           "Before starting there will be two practice examples of the sort of task you'll be doing. Remember, you'll have to read and respond quickly."]
    return render_template('instruct.html', title=title, stim=stm, next=next_page)


@app.route('/next_trial', methods=['GET'])
def next_trial():
    t = int(request.args.get('trial'))+1
    if request.args.get('exp_state') == "TF_TRIAL":
        if t <= n_trials:
            return redirect(url_for('ready', PROLIFIC_PID=request.args.get('PROLIFIC_PID'),
                                    SESSION_ID=request.args.get('SESSION_ID'), exp_state="TF_TRIAL", trial=t))
        else:
            subj = Subject.query.filter_by(prolific_id=request.args.get('PROLIFIC_PID')).first()
            subj.block1_complete = True
            db.session.add(subj)
            db.session.commit()
            return redirect(url_for('ready', PROLIFIC_PID=request.args.get('PROLIFIC_PID'),
                                    SESSION_ID=request.args.get('SESSION_ID'), exp_state="FELICITY_PRACTICE", trial=1))

    elif request.args.get('exp_state') == "FELICITY_TRIAL":
        if t <= n_fel_trials:
            return redirect(url_for('ready', PROLIFIC_PID=request.args.get('PROLIFIC_PID'),
                                    SESSION_ID=request.args.get('SESSION_ID'), exp_state="FELICITY_TRIAL", trial=t))
        else:
            subj = Subject.query.filter_by(prolific_id=request.args.get('PROLIFIC_PID')).first()
            subj.block2_complete = True
            db.session.add(subj)
            db.session.commit()
            return redirect(url_for('ready', PROLIFIC_PID=request.args.get('PROLIFIC_PID'),
                                    SESSION_ID=request.args.get('SESSION_ID'), exp_state="AQ", trial=1))

    elif request.args.get('exp_state') == "FELICITY_PRACTICE":
        if t == 3:
            state = "FELICITY_TRIAL"
            trl = 1
        else:
            state = "FELICITY_PRACTICE"
            trl = t
        return redirect(url_for('ready', PROLIFIC_PID=request.args.get('PROLIFIC_PID'),
                                SESSION_ID=request.args.get('SESSION_ID'), exp_state=state, trial=trl))

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

    elif request.args.get('exp_state') == "AQ":
        return redirect(url_for('ready', PROLIFIC_PID=request.args.get('PROLIFIC_PID'),
                                SESSION_ID=request.args.get('SESSION_ID'), exp_state="DEMOS"))


msgs = {e_state: {var: None for var in [1, 2, 'next']} for e_state in ['TRIAL_PRACTICE', 'TF_TRIAL',
                                                                       'FELICITY_PRACTICE', 'FELICITY_TRIAL', 'AQ',
                                                                       "DEMOS"]}

msgs["TRIAL_PRACTICE"][1] = "Okay, one more practice example"
msgs["TRIAL_PRACTICE"][2] = "Press the space bar to continue, then place your fingers on the [f] and [j] keys.... "
msgs["TRIAL_PRACTICE"]['next'] = "/story"
msgs["TF_TRIAL"][1] = "Okay, get ready for the next story."
msgs["TF_TRIAL"][2] = "Press the space bar to continue, then place your fingers on the [f] and [j] keys.... "
msgs["TF_TRIAL"]['next'] = "/story"
msgs["FELICITY_PRACTICE"][1] = "Great Job!"
msgs["FELICITY_PRACTICE"][2] = "Press the space bar to continue.... "
msgs["FELICITY_PRACTICE"]['next'] = {1: "/felicity_instr", 2: "/fel_story"}
msgs["FELICITY_TRIAL"][1] = "Okay, get ready for the next story."
msgs["FELICITY_TRIAL"][2] = "Press the space bar to continue.... "
msgs["FELICITY_TRIAL"]['next'] = "/fel_story"
msgs["AQ"][1] = "Great Job! - Now you will answer some short questions about yourself."
msgs["AQ"][2] = "Press the space bar to continue.."
msgs["AQ"]["next"] = "/aq_10"
msgs["DEMOS"][1] = "Thank You! - You're almost done. Just a few more short questions about yourself."
msgs["DEMOS"][2] = "Press the space bar to continue.."
msgs["DEMOS"]["next"] = "/demos"


@app.route('/ready', methods=['GET', 'POST'])
def ready():
    if request.args.get('exp_state') != "FELICITY_PRACTICE":
        next_pg = msgs[request.args.get('exp_state')]['next']
    else:
        next_pg = msgs[request.args.get('exp_state')]['next'][int(request.args.get('trial'))]
    if (request.args.get('exp_state') in ["TF_TRIAL", "FELICITY_TRIAL"] ) & (request.args.get('trial') == "1"):
        m1="Great Job. Now we will begin this part of the experiment"
    else:
        m1 = msgs[request.args.get('exp_state')][1]

    return render_template('message.html', msg1=m1, msg2=msgs[request.args.get('exp_state')][2], next=next_pg)


@app.route('/story', methods=['GET', 'POST'])
def story():
    if request.method == 'GET':
        if request.args.get('exp_state') != "TRIAL_PRACTICE":
            t_dat = Trial.query.filter_by(prolific_id=request.args.get('PROLIFIC_PID'),
                                          trial_num=int(request.args.get('trial'))).first()
            story = stim[t_dat.trial_type][str(t_dat.scenario)]['belief_manip'][t_dat.belief_type]
            ascrip = stim[t_dat.trial_type][str(t_dat.scenario)]['ascription'][t_dat.ascription_type]

            return render_template('story.html', s1=story[0], s2=story[1], s3=story[2], s4=story[3],
                                   target=ascrip['target'], correct=ascrip['crrct_answr'],
                                   trl=int(request.args.get('trial')), ttype=t_dat.trial_type)
        else:  # Practice
            if int(request.args.get("trial")) <= 10:
                t_dat = Practice.query.filter_by(prolific_id=request.args.get('PROLIFIC_PID'),
                                                 trial_num=int(request.args.get('trial'))).first()
                story = literal_eval(t_dat.prompt)
                return render_template('story.html', s1=story[0], s2=story[1], s3=story[2], s4=story[3],
                                       target=t_dat.target, correct=t_dat.correct_answer, trl=t_dat.trial_num,
                                       ttype=t_dat.trial_type)
            else:
                return redirect(url_for('ready', PROLIFIC_PID=request.args.get('PROLIFIC_PID'),
                                        SESSION_ID=request.args.get('SESSION_ID'), exp_state="TF_TRIAL", trial=1))

    if request.method == 'POST':
        sub_dat = request.get_json()
        # If it's not a practice trial
        if sub_dat['trl_type'] != 'story_practice':
            t_dat = Trial.query.filter_by(prolific_id=sub_dat['PROLIFIC_PID'],
                                          trial_num=int(sub_dat['trl'])).first()
            t_dat.correct = [True if sub_dat['keys_pressed'][-1].lower() == t_dat.correct_answer else False][0]
            t_dat.ip_addy = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr) # str(request.remote_addr)
        else:
            t_dat = Practice.query.filter_by(prolific_id=sub_dat['PROLIFIC_PID'],
                                             trial_num=int(sub_dat['trl'])).first()
            t_dat.correct = True

        t_dat.target_onset = datetime.fromtimestamp(sub_dat['target_onset'] / 1000.0)
        t_dat.response_key = str(sub_dat['keys_pressed'])
        t_dat.response_onset = datetime.fromtimestamp(sub_dat['rt'][-1] / 1000.0)
        db.session.add(t_dat)
        db.session.commit()

        return make_response("200")


@app.route('/felicity_instr')
def felicity_instr():
    title = "Phase 2 Instructions"
    stm = ["In the next part of the experiment you will be asked to judge whether things that people say sound weird or normal.",
           "Here's an example of what we mean.<br>Suppose that your friend has three apples in front of him and after looking at them, he says, \"I have an apple in front of me.\"  <br>That's a weird thing to say.  It's true that there is a apple in front of him, but it sounds weird because there's not just one apple, there are actually three.  <br>A more normal thing to say would be \"I have three apples in front of me.\"",
           "Here's another example.<br> Suppose that Mary got married and then had a baby two years later. Somebody then says, \"My friend Mary had a baby and got married.\"<br> Again, this is technically true because she did do both of those things.  But, it sounds weird because it seems to imply that she had the baby first and got married second, but she actually got married first and had the baby later. <br> A more normal thing to say would be \"Mary got married and had a baby.\"",
           "Here's one last example.<br> Suppose Bruce accidentally hit his friend's hand with a hammer during a construction project.  Later somebody describes what happens by saying, \"Bruce broke a finger.\" <br> Again, this might be considered weird to say, because it seems to imply that Bruce broke his own finger, but he actually broke someone else's finger.  However, despite sounding weird, this sentence is technically true.",
           "In this part of the experiment you will read a number of stories, and after each story we will give you a statement that somebody made about the story.  <br>Your job is to judge whether the statement sounds weird or normal.",
           "Please try to remember that whether or not a sentence is true or false is a completely separate question from whether or not the sentence sounds normal or weird. <br>Some true sentences can sound weird, and some false sentences can sound normal.<br>",
           " Before starting, we want to make sure you understood the instructions by giving you some example questions."]
    next_pg = "/fel_story"
    return render_template('instruct.html', title=title, stim=stm, next=next_pg)


@app.route('/fel_story', methods=['GET', 'POST'])
def fel_story():
    if request.method == 'GET':
        if request.args.get('exp_state') == "FELICITY_TRIAL":
            t_dat = Felicity.query.filter_by(prolific_id=request.args.get('PROLIFIC_PID'),
                                            block2_trial_num=int(request.args.get('trial'))).first()
            story = stim['test'][str(t_dat.fel_scenario)]['belief_manip'][t_dat.fel_belief_type]
            ascrip = stim['test'][str(t_dat.fel_scenario)]['ascription'][t_dat.fel_ascription_type]
            return render_template('fel_story.html', s1=story[0], s2=story[1], s3=story[2], s4=story[3],
                                   target=ascrip['target'], correct=ascrip['crrct_answr'],
                                   trl=int(request.args.get('trial')), ttype='test')

        elif request.args.get('exp_state') == "FELICITY_PRACTICE":
            story = fel_practice[int(request.args.get('trial'))]['story']
            target = fel_practice[int(request.args.get('trial'))]['target']
            explain = fel_practice[int(request.args.get('trial'))]['explain']
            correct = fel_practice[int(request.args.get('trial'))]['correct']
            return render_template("fel_practice.html", s1=story[0], s2=story[1], s3=story[2], s4=story[3],
                                   target=target, explain=explain, correct=json.dumps(correct))

    if request.method == 'POST':
        sub_dat = request.get_json()
        t_dat = Felicity.query.filter_by(prolific_id=sub_dat['PROLIFIC_PID'],
                                         block2_trial_num=int(sub_dat['trl'])).first()
        t_dat.felicity_rating = int(sub_dat['rating'])
        db.session.add(t_dat)
        db.session.commit()

        return make_response("200")


@app.route('/aq_10', methods=['GET', 'POST'])
def aq_10():
    if request.method == 'GET':
        items = ["I often notice small sounds when others do not.",
                 "I usually concentrate more on the whole picture rather than the small details.",
                 "I find it easy to do more than one thing at once.",
                 "If there is an interruption, I can switch back to what I was doing very quickly.",
                 "I find it easy to “read between the lines” when someone is talking to me.",
                 "I know how to tell if someone listening to me is getting bored.",
                 "When I’m reading a story I find it difficult to work out the characters’ intentions.",
                 "I like to collect information about characters of things (e.g. types of car, types of bird, types of train, types of plant, etc.)",
                 "I find it easy to work out what someone is thinking or feeling just by looking at their face.",
                 "I find it difficult to work out people’s intentions."]
        return render_template('aq_10.html', q_items=items)
    if request.method == 'POST':
        s_dat = request.get_json()
        t_dat = AutismScore.query.filter_by(prolific_id=s_dat['prolific_id']).first()
        t_dat.AQ_rating_1=s_dat['AQ_rating_1']
        t_dat.AQ_rating_2=s_dat['AQ_rating_2']
        t_dat.AQ_rating_3=s_dat['AQ_rating_3']
        t_dat.AQ_rating_4=s_dat['AQ_rating_4']
        t_dat.AQ_rating_5=s_dat['AQ_rating_5']
        t_dat.AQ_rating_6=s_dat['AQ_rating_6']
        t_dat.AQ_rating_7=s_dat['AQ_rating_7']
        t_dat.AQ_rating_8=s_dat['AQ_rating_8']
        t_dat.AQ_rating_9=s_dat['AQ_rating_9']
        t_dat.AQ_rating_10=s_dat['AQ_rating_10']

        subj = Subject.query.filter_by(prolific_id=s_dat['prolific_id']).first()
        subj.block3_complete = True
        db.session.add(t_dat, subj)
        db.session.commit()
        return make_response("200")


@app.route('/demos', methods=['GET', 'POST'])
def demos():
    if request.method == 'GET':
        return render_template('demos.html')
    if request.method == "POST":
        s_dat = request.get_json()
        t_dat = Demographic.query.filter_by(prolific_id=s_dat['prolific_id']).first()
        t_dat.age = int(s_dat['age'])
        t_dat.gender = s_dat['gender']
        t_dat.ethnicity = s_dat['race']
        t_dat.education = s_dat['education']
        t_dat.diag = s_dat['diag']
        db.session.add(t_dat)
        subj = Subject.query.filter_by(prolific_id=s_dat['prolific_id']).first()
        subj.email = s_dat['email']
        db.session.add(subj)
        db.session.commit()
        return make_response("200")


@app.route('/debrief', methods=["GET", "POST"])
def debrief():
    if request.method =='GET':

        return render_template('debrief.html', cc=comp_code)
    if request.method == 'POST':
        s_dat = request.get_json()
        t_dat = Subject.query.filter_by(prolific_id=s_dat['prolific_id']).first()
        t_dat.feedback = s_dat['feedback']
        t_dat.completion_code = comp_code
        d_dat = Demographic.query.filter_by(prolific_id=s_dat['prolific_id']).first()
        d_dat.autism_exp = s_dat['autist_experience']
        db.session.add(t_dat)
        db.session.add(d_dat)
        db.session.commit()
        return make_response("200")



if __name__ == '__main__':
    app.run()
