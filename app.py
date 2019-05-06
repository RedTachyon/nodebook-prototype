from flask import Flask, render_template, request, redirect, jsonify, abort
from flask_cors import CORS
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

import json

import models

from utils import query_to_dict

app = Flask(__name__)
CORS(app)

# TODO: Add images


@app.route('/api', methods=['GET'])
def api_home():
    return "This is a barebones  API home screen."


@app.route('/api/reset', methods=['GET'])
def reset_data():
    models.initialize()

    # Create an experiment for class_id=1
    experiment_id = models.create_questionnaire(
        ["Socio1", "Scalar2", "Socio3"],
        [0, 1, 1], [3, 3, 1], 1,
        ["sociometric", "scalar", "sociometric"]
    )
    models.push_questionnaire(experiment_id, 1)

    # Create a response
    models.update_results(1, experiment_id, [[], 2, [6]])
    models.update_results(2, experiment_id, [[1, 6, 7], 3, [1]])

    return "Database has been reset", 201


@app.route('/api/teacher/create_class/<teacher_id>', methods=['POST'])
def api_create_class(teacher_id):
    """
     JSON format:
     {"name": ..., "description": ...}
    """
    info = request.json

    class_id = models.create_class(info['name'], teacher_id, info['description'])
    return class_id


@app.route('/api/teacher/get_classes/<teacher_id>', methods=['GET'])
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
    classes = models.get_classes(teacher_id)

    classes_dict = query_to_dict(classes, 'classes', [(0, 'id'), (1, 'name'), (3, 'description')])

    return jsonify(classes_dict)


@app.route('/api/teacher/get_students/<class_id>', methods=['GET'])
def api_students(class_id):
    students = models.get_students_in_class(class_id)

    students_dict = query_to_dict(students, 'students', [(0, 'id'), (1, 'name')])

    return jsonify(students_dict)


@app.route('/api/teacher/list_experiments/<class_id>', methods=['GET'])
def api_list_experiments(class_id):
    experiments = models.list_experiments(class_id)
    # print(experiments)
    experiments_dict = query_to_dict(experiments, "experiments", [(0, 'id'), (1, 'date_created')])

    return jsonify(experiments_dict)


@app.route('/api/teacher/experiment_details/<experiment_id>', methods=['GET'])
def api_experiment_details(experiment_id):
    info = models.get_experiment_details(experiment_id)

    info_dict = json.loads(info)

    return jsonify(info_dict)


@app.route('/api/teacher/experiment_replies/<experiment_id>', methods=['GET'])
def api_experiment_replies(experiment_id):
    replies = models.get_teacher_experiment_replies(experiment_id)

    replies_dict = json.loads(replies)

    return jsonify(replies_dict)


@app.route('/api/teacher/get_experiments/<class_id>', methods=['GET'])
def api_class_experiments(class_id):
    experiments = models.get_experiments(class_id)

    experiments_dict = {'experiments': []}

    for exp in experiments:
        experiments_dict['experiments'].append(
            {
                'id': exp[0],
                'info': models.json.loads(exp[1]),
                'replies': models.json.loads(exp[2])['replies'],
                'date_created': exp[4],
                'finished': exp[5],
            }
        )

    return jsonify(experiments_dict)


@app.route('/api/teacher/create_experiment/<class_id>', methods=['POST'])
def api_create_experiment(class_id):
    """
    JSON format:
    {"questions": ["Text1", "Text2", "Text3"],
     "mins": [0, 1, 1],
     "maxs": [5, 1, 3],
     "types": ["sociometric", "sociometric", "scale"]

    """
    info = request.json

    if not ('questions' in info and 'mins' in info and 'maxs' in info and 'type' in info):
        return "Malformed input", 400

    # if info['type'] not in ('sociometric', 'scale'):
    #     return "Wrong type", 400

    experiment_id = models.create_questionnaire(info['questions'], info['mins'], info['maxs'], class_id, info['types'])

    models.push_questionnaire(experiment_id, class_id)

    return jsonify(info)


@app.route('/api/teacher/save_template/<category_id>', methods=['POST'])
def api_save_template(category_id):
    content = json.dumps(request.json)
    models.save_template(category_id, content)
    return content, 201


@app.route('/api/teacher/load_templates/<category_id>', methods=['GET'])
def api_load_templates(category_id):
    templates = models.load_templates(category_id)
    # print(templates[0])
    templates = map(lambda x: x[0], templates)
    templates = list(map(json.loads, templates))
    response = {"templates": templates}
    return jsonify(response)


@app.route('/api/teacher/new_category/<teacher_id>', methods=['POST'])
def api_create_category(teacher_id):
    info = request.json

    name = info['name']

    id_ = models.new_category(teacher_id, name)

    return id_


@app.route('/api/teacher/list_categories/<teacher_id>', methods=['GET'])
def api_list_categories(teacher_id):
    categories = models.all_categories(teacher_id)

    cat_dict = query_to_dict(categories, "categories", [(0, "id"), (1, "name")])

    return cat_dict


# @app.route('/api/teacher/get_templates/<category_id>', methods=['GET'])
# def api_get_templates(category_id):
#     templates = models.load_templates(category_id)
#
#     templates_dict = query_to_dict(templates, "templates", [(0, "id"), (1, "content")])
#
#     return jsonify(templates_dict)



################
# STUDENT PART #
################


@app.route('/api/student/get_questionnaires/<student_id>', methods=['GET'])
def api_questionnaires(student_id):
    experiments = models.get_pending_experiments(student_id)

    exp_dict = query_to_dict(experiments, 'experiments', [(0, 'id'), (1, 'date')])
    return jsonify(exp_dict)


@app.route('/api/student/questionnaire_info/<student_id>/<experiment_id>', methods=['GET'])
def api_questionnaire_details(student_id, experiment_id):
    info, students = models.get_experiment_info(student_id, experiment_id)

    students_dicts = [{'name': s[1], 'id': s[0]} for s in students]

    res_dict = {'info': models.json.loads(info), 'students': students_dicts}

    # print(students)
    # print(json.loads(info))
    return jsonify(res_dict)


@app.route('/api/student/questionnaire_reply/<student_id>/<experiment_id>', methods=['POST'])
def api_questionnaire_reply(student_id, experiment_id):
    """
    student_response should be like
    [ [3, 5], 2, [7], [] ]
    If questions 0, 2, 3 were sociometric and question 1 was scale

    aka the input json has format
    {"responses":
      [
        [3, 5],
        2,
        [7],
        []
      ]
    }

    """

    if not models.check_experiment_exists(student_id, experiment_id):
        abort(400, description='Experiment does not exist')

    info = request.json

    student_response = info["responses"]

    models.update_results(student_id, experiment_id, student_response)

    return 'Response submitted', 201


########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################


@app.route('/', methods=['GET'])
def home():
    teachers = models.get_teachers()

    students = models.get_all_students()

    return render_template('index.html', teachers=teachers, students=students)

#
# @app.route('/teacher/<teacher_id>', methods=['GET', 'POST'])
# def teacher_home(teacher_id):
#
#     if request.method == 'POST':
#         name = request.form.get('name')
#         description = request.form.get('desc')
#         models.create_class(name, teacher_id, description)
#
#     classes = models.get_classes(teacher_id)
#
#     return render_template('teacher_home.html', classes=classes, teacher_id=teacher_id)
#
#
# @app.route('/class/<teacher_id>/<class_id>', methods=['GET', 'POST'])
# def class_home(teacher_id, class_id):
#
#     if request.method == 'POST':
#         questions = [request.form.get('q1'), request.form.get('q2')]
#
#         mins = [request.form.get('min1'), request.form.get('min2')]
#
#         maxs = [request.form.get('max1'), request.form.get('max2')]
#
#         experiment_id = models.create_questionnaire(questions, mins, maxs, class_id)
#         models.push_questionnaire(experiment_id, class_id)
#
#     experiments = models.get_experiments(class_id)
#     students = models.get_students_in_class(class_id)
#
#     return render_template('class_home.html',
#                            experiments=experiments,
#                            class_id=class_id,
#                            teacher_id=teacher_id,
#                            students=students)
#
#
# @app.route('/student/<student_id>')
# def student_home(student_id):
#     experiments = models.get_pending_experiments(student_id)
#
#     return render_template('student_home.html',
#                            experiments=experiments,
#                            student_id=student_id)
#
#
# @app.route('/experiment/<student_id>/<experiment_id>', methods=['GET', 'POST'])
# def experiment_screen(student_id, experiment_id):
#     info, students = models.get_experiment_info(student_id, experiment_id)
#
#     result_dict = models.json.loads(info[0][0])
#     print(result_dict)
#
#     if request.method == 'POST':
#         students_chosen = []
#         for answer_student_id in request.form:
#             students_chosen.append(answer_student_id)
#
#         models.update_results(student_id, experiment_id, students_chosen)
#         return redirect('/student/%s' % student_id)
#
#     return render_template('experiments_screen.html',
#                            results=info[0][0],
#                            students=students,
#                            student_id=student_id,
#                            experiment_id=experiment_id)


if __name__ == '__main__':
    app.run(debug=True)
