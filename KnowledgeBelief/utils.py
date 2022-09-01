import pandas as pd
import numpy as np
import json
import random
from .models import UniqueId
from . import db
import string


# Add subject IDs to database
def add_subjects(n=20):
    for i in range(n):
        pid = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
        db.session.add(UniqueId(unique_code=pid, used=False))
    db.session.commit()
    return print(f'{n} new access IDs have been added to the database for use. ')


def get_access_code():
    return UniqueId.query.filter_by(used=False).all()


# practice
def make_practice():
    n_tf_pract = 8
    n_story_pract = 2
    p1 = [
        "Kevin is out grocery shopping at the local market. His wife told him to get sourdough bread and pasta for dinner that evening.",
        "At the market, Kevin picks up some pasta, but he cannot find any sourdough bread anywhere. He looks up and down every aisle and then finally asks someone who works at the market.",
        "It turns out that the bakery at the market no longer makes sourdough bread because it was never very popular. ",
        "Kevin goes home without bread of any kind. His wife is slightly annoyed."
        ]
    p1_target = "Kevin asked someone at the store if they sold bread."
    p2 = [
        "Sara's younger sister is late for dance class. Sara has a scooter that she could lend her sister for the afternoon.",
        "The scooter is brand-new and will get Sara's sister to her dance class right on time. But Sara wants to use her scooter to get to her friend's house for dinner later on.",
        "Sara doesn't think that her sister's dance class will be over in time for her to also be able to use the scooter to get to dinner.",
        "Sara doesn't lend the scooter to her sister. Her sister walks to dance class and is late."
        ]
    p2_target = "Sara wanted to take her scooter to the park."
    tf_prac = ["False"] * int(n_tf_pract/2) + ["True"] * int(n_tf_pract/2)
    random.shuffle(tf_prac)
    ca = ['f' if tf_p == 'False' else 'j' for tf_p in tf_prac]
    [ca.append(x) for x in ['j', 'f']]
    pract = {'trial_num': list(range(1, sum([n_tf_pract,n_story_pract])+1)),
             'trial_type':['tf_practice'] * n_tf_pract + ['story_practice']* n_story_pract,
             'prompt': tf_prac + [p1, p2],
             'correct': None,
             'target': [None]*n_tf_pract + [p1_target, p2_target],
             'correct_answer': ca,
             'response_key':None,
             'target_onset': None,
             'response_onset': None,
             }
    return pd.DataFrame(pract)


# trials
def make_trials():
    vig_numbers = list(range(1, 13))
    bel_types = ['TB', 'FB', 'IG']
    ascrip_types = ['Knows', 'Thinks']
    # assign scenarios and shuffle
    s1 = pd.DataFrame({
        'trial_num': None,
        'correct': None,
        'trial_type': 'test',
        'scenario': vig_numbers,
        'belief': None,
        'ascription': None,
        'crrct_answer': None,
        'target_onset': None,
        'response_onset': None,
        'response_key': None,
    }).sample(frac=1)
    # balance belief types and shuffle
    s1['belief'] = np.repeat(bel_types, len(vig_numbers) / len(bel_types))
    # balance ascription types across belief types
    aa = np.repeat(ascrip_types, (len(vig_numbers) / len(bel_types))/len(ascrip_types))
    for bb in bel_types:
        np.random.shuffle(aa)
        s1.loc[s1.belief == bb, 'ascription'] = aa

    s1 = s1.sample(frac=1)
    # add distractors
    s2 = s1.copy()
    s2['trial_type'] = 'distractor'
    s3 = pd.concat([s1, s2], ignore_index=True).sample(frac=1).reset_index(drop=True)
    s3['trial_num'] = range(1, len(s3) + 1)
    # add correct answers
    s3.loc[s3.belief == 'TB', 'crrct_answer'] = 'j'
    s3.loc[s3.belief != 'TB', 'crrct_answer'] = 'f'

    return s3


# Felicity
def make_felicity(trls):
    xx = trls.loc[trls.trial_type == 'test'].sample(frac=1)
    fel = pd.DataFrame({'b2_trial_num': list(range(1, 13)),
                        'b1_trial_num': xx.trial_num.values,
                        'fel_scenario': xx.scenario.values,
                        'fel_belief_type': xx.belief.values,
                        'fel_ascription_type': xx.ascription.values,  # "knows" or "thinks"
                        'felicity_rating': None})
    return fel


# all subject trials
def randomize_trials():
    prac = make_practice()
    trls = make_trials()
    fels = make_felicity(trls)
    return prac, trls, fels


# Felicity Practice
fel_p1 = ["John owed a lot of money to a bartender at a local bar.",
          "One day he went into the bar to talk to the bartender about his debt.",
          "While John was there, he accidentally slipped on some ice near the counter and fell, breaking his arm and wrist.",
          "Feeling bad for him, the bartender told him not to worry about the money he owed."]
fel_p1_target = "John went into the bar where the guy works and broke some bones."
fel_p1_expln = "Even though it is true, it should sound weird to say that John broke some bones because it seems to imply that he settled his debt by breaking someone else's bones, not his own."

fp1 = {'story': fel_p1, 'target': fel_p1_target, 'explain':fel_p1_expln, 'correct': [1, 2, 3]}

fel_p2 = ["Carrie needed a hammer to hang a painting she just bought,",
          "so she went over to David's house and borrowed a hammer from him.",
          "She used the hammer to hang the painting.", "Then returned the hammer to David."]

fel_p2_target = "Carrie didn't borrow a hammer from David."
fel_p2_expln = "Even though it is false, this statement sounds completely normal. Saying this sentence doesn't imply anything strange at all - it is just straightforwardly false. This statement sounded normal but was false."

fp2 = {'story': fel_p2, 'target': fel_p2_target, 'explain': fel_p2_expln, 'correct': [5, 6, 7]}

fel_practice = {1: fp1, 2: fp2}
