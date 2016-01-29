#!/usr/bin/env python

import os
import random
import shutil
import yaml

week = 2
probs = [1, 2, 3]
npeers = 2

# This is the root directory of the ansible config
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

assign_path = os.path.join(root, '..', 'assignments', 'submitted')
peer_assess_path = os.path.join(root, '..', 'peer_assessments')

with open(os.path.join(root, 'users.yml')) as f:
    all_users = yaml.load(f)

users = all_users['jupyterhub_testers']
random.shuffle(users)

data = {'users': users}
save_path = os.path.join(root, 'week{}.yml'.format(week))
with open(save_path, 'w') as f:
    f.write(yaml.dump(data))

users_periodic = users * 2

week_path = os.path.join(peer_assess_path, 'Week{}'.format(week))
if os.path.exists(week_path):
    shutil.rmtree(week_path)
os.makedirs(week_path)

for i, user in enumerate(users):

    user_path = os.path.join(week_path, user)
    os.makedirs(user_path)

    for j in range(npeers):

        peer_path = os.path.join(user_path, 'Student{}'.format(j))

        for prob in probs:

            prob_path = os.path.join(peer_path, 'Problem{}'.format(prob))
            os.makedirs(prob_path)

            src_path = os.path.join(
                assign_path,
                users_periodic[i + j + 1], ### use peer
                'w{}p{}'.format(week, prob),
                'w{}p{}.ipynb'.format(week, prob)
                )
            shutil.copy(src_path, prob_path)
