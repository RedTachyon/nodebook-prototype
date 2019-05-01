from flask import Flask, render_template, request, redirect, jsonify, abort
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

import sqlite3 as sql
import datetime
import json

from models import get_classes, get_teachers, get_experiments, create_class, create_questionnaire, get_students_in_class
from models import get_all_students, push_questionnaire, get_pending_experiments, get_experiment_info, update_results
from models import check_experiment_exists, initialize

from utils import query_to_dict

app = Flask(__name__)


@app.route('/api/reset', methods=['GET'])
def reset_data():
    initialize()
    return "Database has been reset"

@app.route('/api/get_classes/<teacher_id>', methods=['GET'])
def api_classes(teacher_id):
    """
    {
    "classes": [
        {
          "description": "The most basic class",
          "id": 1,
          "name": "1A"
        },
        {
          "description": "The most basic class",
          "id": 2,
          "name": "2A"
        },
        {
          "description": "An empty class cuz I'm lazy",
          "id": 5,
          "name": "10F"
        }
      ]
    }

    """
    classes = get_classes(teacher_id)

    classes_dict = query_to_dict(classes, 'classes', [(0, 'id'), (1, 'name'), (3, 'description')])

    return jsonify(classes_dict)


@app.route('/api/get_students/<class_id>', methods=['GET'])
def api_students(class_id):
    students = get_students_in_class(class_id)

    students_dict = query_to_dict(students, 'students', [(0, 'id'), (1, 'name')])

    return jsonify(students_dict)


@app.route('/api/get_experiments/<class_id>')
def api_class_experiments(class_id):
    experiments = get_experiments(class_id)

    # experiments_dict = query_to_dict(experiments, 'experiments', [
    #     (0, 'id'),
    #     (1, 'info'),
    #     (2, 'replies'),
    #     (4, 'date_created'),
    #     (5, 'finished')
    # ])

    experiments_dict = {'experiments': []}
    for exp in experiments:
        experiments_dict['experiments'].append(
            {
                'id': exp[0],
                'info': json.loads(exp[1]),
                'replies': json.loads(exp[2])['replies'],
                'date_created': exp[4],
                'finished': exp[5]
            }
        )

    return jsonify(experiments_dict)


################
# STUDENT PART #
################


@app.route('/api/get_questionnaires/<student_id>', methods=['GET'])
def api_questionnaires(student_id):
    experiments = get_pending_experiments(student_id)

    exp_dict = query_to_dict(experiments, 'experiments', [(0, 'id'), (1, 'date')])
    return jsonify(exp_dict)


@app.route('/api/questionnaire/<student_id>/<experiment_id>', methods=['GET'])
def api_questionnaire_details(student_id, experiment_id):
    info, students = get_experiment_info(student_id, experiment_id)
    # info = json.loads(info[0])

    students_dicts = [{'name': s[1], 'id': s[0]} for s in students]

    res_dict = {'info': json.loads(info[0][0]), 'students': students_dicts}

    # print(students)
    print(json.loads(info[0][0]))
    return jsonify(res_dict)


@app.route('/api/questionnaire_reply/<student_id>/<experiment_id>', methods=['POST'])
def api_questionnaire_reply(student_id, experiment_id):
    """
    Usage: pass selected student id's as the keys of the query (?), with the value 'true'
    .../api/questionnaire_reply/X/Y?1=true&5=true&10=true
    """

    if not check_experiment_exists(student_id, experiment_id):
        abort(400, description='Experiment does not exist')

    args = [arg for arg in request.args.lists()]

    idx = []
    for id_, value in args:
        if value[0] == 'true':
            idx.append(id_)

    print(idx)

    update_results(student_id, experiment_id, idx)

    return 'Response submitted'


########################################################################################################################

@app.route('/', methods=['GET'])
def home():
    teachers = get_teachers()

    students = get_all_students()

    return render_template('index.html', teachers=teachers, students=students)


@app.route('/teacher/<teacher_id>', methods=['GET', 'POST'])
def teacher_home(teacher_id):

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('desc')
        create_class(name, teacher_id, description)

    classes = get_classes(teacher_id)

    return render_template('teacher_home.html', classes=classes, teacher_id=teacher_id)


@app.route('/class/<teacher_id>/<class_id>', methods=['GET', 'POST'])
def class_home(teacher_id, class_id):

    if request.method == 'POST':
        questions = [request.form.get('q1'), request.form.get('q2')]

        mins = [request.form.get('min1'), request.form.get('min2')]

        maxs = [request.form.get('max1'), request.form.get('max2')]

        experiment_id = create_questionnaire(questions, mins, maxs, class_id)
        push_questionnaire(experiment_id, class_id)

    experiments = get_experiments(class_id)
    students = get_students_in_class(class_id)

    return render_template('class_home.html',
                           experiments=experiments,
                           class_id=class_id,
                           teacher_id=teacher_id,
                           students=students)


@app.route('/student/<student_id>')
def student_home(student_id):
    experiments = get_pending_experiments(student_id)

    return render_template('student_home.html',
                           experiments=experiments,
                           student_id=student_id)


@app.route('/experiment/<student_id>/<experiment_id>', methods=['GET', 'POST'])
def experiment_screen(student_id, experiment_id):
    info, students = get_experiment_info(student_id, experiment_id)

    result_dict = json.loads(info[0][0])
    print(result_dict)

    if request.method == 'POST':
        students_chosen = []
        for answer_student_id in request.form:
            students_chosen.append(answer_student_id)

        update_results(student_id, experiment_id, students_chosen)
        return redirect('/student/%s' % student_id)

    return render_template('experiments_screen.html',
                           results=info[0][0],
                           students=students,
                           student_id=student_id,
                           experiment_id=experiment_id)


if __name__ == '__main__':
    app.run(debug=True)
