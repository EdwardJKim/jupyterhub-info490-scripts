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
        print('Usage: ./nbmerge/nbmerge.py --week=<week number> --nnb=<number of notebooks to grade>')
        print('For 5 students and 3 problems per student, nnb = 15')

    try:                                
        opts, args = getopt.getopt(argv, "hwp:d", ["help", "week=", "nnb="])
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
        elif opt == '--nnb':
            nnb = int(arg)
        else:
            usage()
            sys.exit(2)

    # This is the root directory of the ansible config
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    users = get_users(os.path.join(root, 'users.yml'), 'jupyterhub_users')

    assess_dir = '/home/jkim575/complete_assessments' 

    for user in users:
        yml_path = os.path.join(assess_dir, user, '{}_Week{}.yml'.format(user, week))
        if os.path.exists(yml_path):
            with open(yml_path) as f:
                data = yaml.load(f)
        else:
            continue

        dweek = data['Week{}'.format(week)]
        ngraded = 0
 
        for peer in dweek:
            for prob in dweek[peer]:
                ngraded += 1

        score = 30.0 * ngraded / nnb

        print("{},{}".format(user, score))

if __name__ == '__main__':
    main(sys.argv[1:])
