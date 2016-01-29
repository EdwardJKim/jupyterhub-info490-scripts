#!/usr/bin/env python

import os
import sys
import io
import random
import shutil
import getopt
import yaml
import nbformat

def get_users(src, group):
    with open(src) as f:
        all_users = yaml.load(f)
    users = all_users['jupyterhub_testers']
    return users

def save_yml(dest, users):
    data = {'users': users}
    with open(dest, 'w') as f:
        f.write(yaml.dump(data))

def clear_week(dest):
    if os.path.exists(dest):
        answer = raw_input('{} exists. Are you sure you want to delete? '
            ''.format(dest))
        if answer == 'y':
            shutil.rmtree(dest)
        else:
            return
    os.makedirs(dest)

def merge_notebooks(filenames):
    merged = None
    for fname in filenames:
        with io.open(fname, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        for i, cell in enumerate(nb.cells):
            if ( 'nbgrader' in cell['metadata'] and
                cell['metadata']['nbgrader']['grade_id'] == 'header'):
                nb.cells.pop(i)
        if merged is None:
            merged = nb
        else:
            # TODO: add an optional marker between joined notebooks
            # like an horizontal rule, for example, or some other arbitrary
            # (user specified) markdown cell)
            merged.cells.extend(nb.cells)
    if not hasattr(merged.metadata, 'name'):
        merged.metadata.name = ''
    merged.metadata.name += "_merged"
    return nbformat.writes(merged)

def nbcopy(src, dest, week, users, npeers=5, probs=3):
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    users_periodic = users * 2
    for i, user in enumerate(users):
        user_path = os.path.join(dest, user)
        os.makedirs(user_path)
        for j in range(1, npeers + 1):
            peer_path = os.path.join(user_path, 'Student{}'.format(j))
            for prob in range(1, probs + 1):
                prob_path = os.path.join(
                    peer_path,
                    'Problem{}'.format(prob)
                    )
                os.makedirs(prob_path)
                src_path = os.path.join(
                    src,
                    users_periodic[i + j + 1],
                    'w{}p{}'.format(week, prob),
                    'w{}p{}.ipynb'.format(week, prob)
                    )
                header = os.path.join(root, 'nbmerge', 'peer_header.ipynb')
                footer = os.path.join(root, 'nbmerge', 'peer_footer.ipynb')
                merged = merge_notebooks([header, src_path, footer])
                dest_path = os.path.join(prob_path, 'w{}p{}.ipynb'.format(week, prob))
                with open(dest_path, 'w') as f:
                    f.write(merged)

def main(argv):

    week = 0

    def usage():
        print('Usage: ./nbmerge/nbmerge.py --week=<week number> --peers=<number of peers>')

    try:                                
        opts, args = getopt.getopt(argv, "hwp:d", ["help", "week=", "peers="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    if len(opts) == 0:
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
        elif opt == '--peers':
            npeers = int(arg)
        else:
            usage()
            sys.exit(2)

    # This is the root directory of the ansible config
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    users = get_users(os.path.join(root, 'users.yml'), 'jupyterhub_testers')
    
    random.shuffle(users)
    
    save_yml(os.path.join(root, 'week{}.yml'.format(week)), users)
    
    peer_assess_path = os.path.join(root, '..', 'peer_assessments')
    week_path = os.path.join(peer_assess_path, 'Week{}'.format(week))
    
    clear_week(week_path)
    
    assign_path = os.path.join(root, '..', 'assignments', 'submitted')
    nbcopy(assign_path, week_path, week, users, npeers=2) ### change npeers for production

if __name__ == '__main__':
    main(sys.argv[1:])
