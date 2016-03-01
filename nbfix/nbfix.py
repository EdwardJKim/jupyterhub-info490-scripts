#!/usr/bin/env python

import os
import sys
import io
import random
import shutil
import getopt
import nbformat

def get_users(src, group):
    with open(src) as f:
        all_users = yaml.load(f)
    users = all_users[group]
    return users

def get_source(filename, grade_id):
    source = None
    with io.open(filename, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    for i, cell in enumerate(nb.cells):
        if ('nbgrader' in cell['metadata'] and
            cell['metadata']['nbgrader']['grade_id'] == grade_id):
            source = nb.cells[i]['source']
    return source

def fix_notebook(filename, grade_id, source):
    with io.open(filename, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    for i, cell in enumerate(nb.cells):
        if ('nbgrader' in cell['metadata'] and
            cell['metadata']['nbgrader']['grade_id'] == grade_id):
            nb.cells[i]['source'] = source
    return nbformat.writes(nb)

def write_notebook(source, filename):
    with io.open(filename, 'w', encoding='utf-8') as f:
        f.write(source)

def main(argv):

    week = 0

    def usage():
        print('Usage: ./nbfix.py --target=<target file> --id=<grade_id> --source=<source file>')

    try:                                
        opts, args = getopt.getopt(argv, "hwp:d", ["help", "target=", "id=", "source="])
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
        elif opt == '--target':
            target = arg
        elif opt == '--id':
            grade_id = arg
        elif opt == '--source':
            source = arg
        else:
            usage()
            sys.exit(2)

    source_code = get_source(source, grade_id)
    if source is None:
        print('{} not found.'.format(grade_id))
        sys.exit(2)
    else:
        updated = fix_notebook(target, grade_id, source_code)
        write_notebook(updated, target)

if __name__ == '__main__':
    main(sys.argv[1:])
