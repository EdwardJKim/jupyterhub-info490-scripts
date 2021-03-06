#!/usr/bin/env python3                                                                                                                    
                                                                                                                                          
import os
import sys
import yaml
import ipywidgets as widgets
from IPython.display import display, clear_output


class RubricWidget(widgets.DOMWidget):
    def __init__(self, nb_path=None, yml_path=None, nproblems=3, **kwargs):                                                                                                         
        """Constructor"""                                                                                                                 
        widgets.DOMWidget.__init__(self, **kwargs) # Call the base.

        self.nproblems = nproblems

        self.nbpath = os.getcwd()
        if nb_path is None:
            nb_path = os.getcwd()
        week, student, problem = nb_path.split('/')[-3:]

        if not (
            week.startswith('Week') and
            student.startswith('Student') and
            problem.startswith('Problem')
            ):
            raise ValueError(
                'The .ipynb file must be in the directory '
                '/home/data_scientist/peer_assessments/Week*/Student*/Problem*'
                )

        self.week = week
        self.student = student
        self.problem = problem

        if yml_path is None:
            self.yml_path = '/home/data_scientist/.info490/grades/{}.yml'.format(week)
        
    def display_rubric(self):

        self.correctness = widgets.RadioButtons(
            description='Correctness ',
            options={
                ('0 points. Code does not run.'): 0,
                ('2 points. Code runs, but does not produce correct '
                 'output. '): 2,
                ('4 points. Code runs, produces correct output, '
                 'but output is difficult to understand.'): 4,
                ('5 points. Code runs, produces correct output, '
                 'and output is easy to understand.'): 5
                }
            )

        self.readability = widgets.RadioButtons(
            description='Readability ',
            options={
                ('0 points. Code is not documented and is impossible to '
                 'understand.'): 0,
                ('2 points. Code is poorly documented, and uses '
                 'non-recommended practices.'): 2,
                ('4 points. Code is documented, but uses non-recommended '
                 'practices'): 4,
                ('5 points. Code is fully documented (as appropriate), '
                 'and uses good programming practices.'): 5
                }
            )

        self.comments = widgets.Textarea(
            description='Comments '
            )

        submit = widgets.Button(description="Submit your assessment")
        validate = widgets.Button(description="Check remaining tasks")

        display(widgets.HTML(value='<b>Assessment Form</b>'))
        display(self.correctness)
        display(self.readability)
        display(self.comments)
        display(submit)
        display(validate)

        submit.on_click(self._on_submit_clicked)                                                                                          
        validate.on_click(self._on_validate_clicked)
                                                                                                                                          
    def _on_submit_clicked(self, b):

        self._print_submitted()
        self._save_submitted(self.yml_path)

    def _print_submitted(self):

        clear_output()
        print('Assessment submitted')
        print('--------------------')
        print('Student: {}'.format(self.student))
        print('Week: {}'.format(self.week))
        print('Problem: {}'.format(self.problem))
        print('Correctness: {}'.format(self.correctness.selected_label))
        print('Readability: {}'.format(self.readability.selected_label))
        print('Comments: {}\n'.format(self.comments.value))
        print('To change your assessment, simply select different values '
              'and click Submit again.')

    def _save_submitted(self, path):

        w = self.week
        s = self.student
        p = self.problem

        if os.path.exists(path):
            with open(path) as f:
                data = yaml.load(f)
            os.remove(path)
        else:
            data = {}

        if w not in data:
            data[w] = {}
        if s not in data[w]:
            data[w][s] = {}
        if p not in data[w][s]:
            data[w][s][p] = {}

        data[w][s][p]['correctness'] = self.correctness.value
        data[w][s][p]['readability'] = self.readability.value
        data[w][s][p]['comments'] = self.comments.value

        with open(path, 'w') as f:
            f.write(yaml.dump(data))

    def _on_validate_clicked(self, b):

        clear_output()

        if not os.path.exists(self.yml_path):
            print("No data found. You haven't graded any peers.")
            return

        with open(self.yml_path) as f:
            data = yaml.load(f)

        done = {}
        todo = {}

        for s in range(5):
            student = 'Student{}'.format(s + 1)
            if student not in data[self.week].keys():
                done[student] = ['']
                todo[student] = ['Problem{}'.format(i + 1) for i in range(self.nproblems)]
                continue
            done[student] = []
            todo[student] = []
            for p in range(self.nproblems):
                problem = 'Problem{}'.format(p + 1)
                if problem in data[self.week][student].keys():
                    done[student].append(problem)
                else:
                    todo[student].append(problem)

        print('Submitted')
        print('---------')
        for s in sorted(done):
            print('{}: {}'.format(s, ', '.join(done[s])))
        print('')
        print('Remaining tasks')
        print('---------------')
        for s in sorted(todo):
            print('{}: {}'.format(s, ', '.join(todo[s])))
