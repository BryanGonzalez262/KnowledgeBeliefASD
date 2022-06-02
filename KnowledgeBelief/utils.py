import pandas as pd
import numpy as np
import json
import random


def randomize_trials():
    trial_types = ['test', 'distractor']
    vig_numbers = list(range(1, 13))
    bel_types = ['TB', 'FB', 'IG']
    ascrip_types = ['Knows', 'Thinks']
    # assign scenarios and shuffle
    s1 = pd.DataFrame({
        'trial_num': None,
        'prompt': None,
        'correct': None,
        'trial_type': 'test',
        'scenario': vig_numbers,
        'belief': None,
        'ascription': None,
        'target': None,
        'crrct_answer': None,
        'target_onset': None,
        'response_onset': None,
        'response_key': None,
    }).sample(frac=1)
    # balance balance acription types and shuffly
    s1['ascription'] = np.repeat(ascrip_types, len(vig_numbers) / len(ascrip_types))
    s1 = s1.sample(frac=1)
    # balance belief types and shuffl
    s1['belief'] = np.repeat(bel_types, len(vig_numbers) / len(bel_types))
    s2 = s1.copy()
    s2['trial_type'] = 'distractor'
    s3 = pd.concat([s1, s2], ignore_index=True).sample(frac=1).reset_index(drop=True)
    s3['trial_num'] = range(1, len(s3) + 1)
    # add practice
    # Adding Practice
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
    n_practice = 8
    s3a = pd.DataFrame({x: None for x in s3.columns.tolist()}, index=range(n_practice))
    s3a.trial_type = ['tf_practice', 'tf_practice', 'tf_practice', 'tf_practice', 'tf_practice', 'tf_practice',
                      'practice', 'practice']
    s3a.trial_num = [999] * n_practice

    tf_prac = ["False"] * 3 + ["True"] * 3
    random.shuffle(tf_prac)
    ca = ['f' if tf_p == 'False' else 'j' for tf_p in tf_prac]
    [ca.append(x) for x in ['j', 'f']]
    [tf_prac.append(prac_prompt) for prac_prompt in [p1, p2]]
    pr_targ = [None] * 6
    [pr_targ.append(p_target) for p_target in [p1_target, p2_target]]

    s3a.prompt = tf_prac
    s3a.target = pr_targ
    s3a.crrct_answer = ca
    s4 = s3a.append(s3, ignore_index=True)
    xx = s4.loc[s4.trial_type == 'test'].sample(frac=1)
    fel = pd.DataFrame({'b2_trial_num': range(1, 13),
                        'b1_trial_num': [int(x) for x in xx.trial_num.values],
                        'fel_scenario': [int(x) for x in xx.scenario.values],
                        'fel_belief_type': xx.belief.values,
                        'fel_ascription_type': xx.ascription.values,  # "knows" or "thinks"
                        'felicity_rating': None})

    return s4, fel