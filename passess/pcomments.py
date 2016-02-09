#!/usr/bin/env python

import os
import sys
import yaml
import getopt

def get_users(src, group):
    with open(src) as f:
        all_users = yaml.load(f)
    users = all_users[group]
    return users

def main(argv):

    week = 0
    ngrade = 0

    def usage():
        print('Usage: ./nbmerge/nbmerge.py --week=<week number> --np=<number of problems>')

    try:                                
        opts, args = getopt.getopt(argv, "hwp:d", ["help", "week=", "np="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    if len(opts) != 2:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()                  
        elif opt == '-d':
            global _debug               
            _debug = 1                  
        elif opt == '--week':
            week = int(arg)
        elif opt == '--np':
            nprob = int(arg)
        else:
            usage()
            sys.exit(2)

    # This is the root directory of the ansible config
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    users_all = get_users(os.path.join(root, 'users.yml'), 'jupyterhub_users')

    assess_dir = '/home/jkim575/complete_assessments' 

    with open('week2.yml') as f:
        users_list = yaml.load(f)

    users_list = users_list['users']

    users_wrapped = users_list * 2

    comments = {k: {} for k in users_list}

    comments_dir = '/home/jkim575/comments/Week{}'.format(week)

    if not os.path.exists(comments_dir):
        os.makedirs(comments_dir)

    for i, user in enumerate(users_list):
        yml_path = os.path.join(assess_dir, user, '{}_Week{}.yml'.format(user, week))
        if os.path.exists(yml_path):
            with open(yml_path) as f:
                data = yaml.load(f)
        else:
            continue

        dweek = data['Week{}'.format(week)]

        for s in range(5):
            skey = 'Student{}'.format(s + 1)
            if skey in dweek:
                dstudent = dweek[skey]
            else:
                continue

            for p in range(nprob):
                pkey = 'Problem{}'.format(p + 1)

                if pkey in dstudent:
                    dproblem = dstudent[pkey]

                peer = users_wrapped[i + s + 1]

                if pkey not in comments[peer]:
                    comments[peer][pkey] = []

                if dproblem['comments'].strip():
                    comments[peer][pkey].append(dproblem['comments'])

        save_path = os.path.join(comments_dir, user)
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        file_path = os.path.join(save_path, 'Week{}.comments'.format(week))
        with open(file_path, 'w') as f:
            stream = yaml.dump(comments[user], default_flow_style=False)
            f.write(stream)

if __name__ == '__main__':
    main(sys.argv[1:])
