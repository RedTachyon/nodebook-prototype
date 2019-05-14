from flask import Flask, render_template, request, jsonify, abort
from flask_cors import CORS

from werkzeug.security import generate_password_hash, check_password_hash

import json
import time

import models

import utils
import authentication as auth

app = Flask(__name__)
CORS(app)

# TODO: Add images


@app.route('/api/', methods=['GET'])
def api_home():
    return "This is a barebones  API home screen.", 418


@app.route('/api/reset', methods=['GET'])
def reset_data():
    models.initialize()

    # Create an experiment for class_id=1
    experiment_id = models.create_questionnaire(
        ["Who do you want to work with this week?", "How happy were you today?", "Who is your best friend?"],
        [0, 1, 1], [3, 3, 1], 1,
        ["sociometric", "scalar", "sociometric"]
    )
    models.push_questionnaire(experiment_id, 1)

    # Create a response
    models.update_results(1, experiment_id, [[], 2, [6]])
    models.update_results(2, experiment_id, [[1, 6, 7], 3, [1]])
    models.update_results(3, experiment_id, [[2, 19, 15], 1, [5]])

    return "Database has been reset", 201


@app.route('/test/file', methods=['POST'])
def upload_file():
    print(request.files)
    print(request.json)
    print(request.args)
    # print(request.files['file'])
    return "Sup"


@app.route('/api/teacher/create_class/<teacher_id>', methods=['POST'])
def api_create_class(teacher_id):
    """
     JSON format:
     {"name": ..., "description": ...}
    """

    allowed_user = int(teacher_id)

    authorized, message = auth.authorize_teacher(allowed_user)
    if not authorized:
        return jsonify(message), 401

    info = request.json

    class_id = models.create_class(info['name'], teacher_id, info['description'])

    message['details'] = "Class created with id %d" % class_id
    return jsonify(message), 201


@app.route('/api/teacher/get_classes/<teacher_id>', methods=['GET'])
def api_classes(teacher_id):
    allowed_user = int(teacher_id)
    authorized, message = auth.authorize_teacher(allowed_user)
    if not authorized:
        return jsonify(message), 401

    classes = models.get_classes(teacher_id)

    classes_dict = utils.query_to_dict(classes, 'classes', [(0, 'id'), (1, 'name'), (3, 'description')])

    return jsonify(classes_dict), 201


@app.route('/api/teacher/get_students/<class_id>', methods=['GET'])
def api_students(class_id):
    class_owner = models.run_simple_query("SELECT teacher_id FROM classes WHERE id = ?", (class_id,))[0][0]

    allowed_user = int(class_owner)
    authorized, message = auth.authorize_teacher(allowed_user)
    if not authorized:
        return jsonify(message), 401

    students = models.get_students_in_class(class_id)

    students_dict = utils.query_to_dict(students, 'students', [(0, 'id'), (1, 'name')])

    return jsonify(students_dict)


@app.route('/api/teacher/list_experiments/<class_id>', methods=['GET'])
def api_list_experiments(class_id):
    class_owner = models.run_simple_query("SELECT teacher_id FROM classes WHERE id = ?", (class_id,))[0][0]

    allowed_user = int(class_owner)
    authorized, message = auth.authorize_teacher(allowed_user)
    if not authorized:
        return jsonify(message), 401

    experiments = models.list_experiments(class_id)
    # print(experiments)
    experiments_dict = utils.query_to_dict(experiments, "experiments", [(0, 'id'), (1, 'date_created')])

    return jsonify(experiments_dict)


@app.route('/api/teacher/experiment_details/<experiment_id>', methods=['GET'])
def api_experiment_details(experiment_id):
    class_owner = models.run_simple_query("SELECT c.teacher_id FROM classes c "
                                          "JOIN experiments e on c.id = e.class_id WHERE e.id = ?",
                                          (experiment_id,))[0][0]

    allowed_user = int(class_owner)
    authorized, message = auth.authorize_teacher(allowed_user)
    if not authorized:
        return jsonify(message), 401

    info = models.get_experiment_details(experiment_id)

    info_dict = json.loads(info)

    return jsonify(info_dict)


@app.route('/api/teacher/experiment_replies/<experiment_id>', methods=['GET'])
def api_experiment_replies(experiment_id):
    class_owner = models.run_simple_query("SELECT c.teacher_id FROM classes c "
                                          "JOIN experiments e on c.id = e.class_id WHERE e.id = ?",
                                          (experiment_id,))[0][0]

    allowed_user = int(class_owner)
    authorized, message = auth.authorize_teacher(allowed_user)
    if not authorized:
        return jsonify(message), 401

    replies = models.get_teacher_experiment_replies(experiment_id)

    replies_dict = json.loads(replies)

    return jsonify(replies_dict)


@app.route('/api/teacher/get_experiments/<class_id>', methods=['GET'])
def api_class_experiments(class_id):
    class_owner = models.run_simple_query("SELECT teacher_id FROM classes WHERE id = ?", (class_id,))[0][0]

    allowed_user = int(class_owner)
    authorized, message = auth.authorize_teacher(allowed_user)
    if not authorized:
        return jsonify(message), 401

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
     "types": ["sociometric", "sociometric", "scale"]}

    """
    class_owner = models.run_simple_query("SELECT teacher_id FROM classes WHERE id = ?", (class_id,))[0][0]

    allowed_user = int(class_owner)
    authorized, message = auth.authorize_teacher(allowed_user)
    if not authorized:
        return jsonify(message), 401

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
    class_owner = models.run_simple_query("SELECT teacher_id FROM template_categories WHERE id = ?", (category_id,))[0][0]

    allowed_user = int(class_owner)
    authorized, message = auth.authorize_teacher(allowed_user)
    if not authorized:
        return jsonify(message), 401

    content = json.dumps(request.json)
    # content = request.json
    models.save_template(category_id, content)
    return content, 201


@app.route('/api/teacher/load_templates/<category_id>', methods=['GET'])
def api_load_templates(category_id):
    class_owner = models.run_simple_query("SELECT teacher_id FROM template_categories WHERE id = ?", (category_id,))[0][0]

    allowed_user = int(class_owner)
    authorized, message = auth.authorize_teacher(allowed_user)
    if not authorized:
        return jsonify(message), 401

    templates = models.load_templates(category_id)

    res_dict = {"templates": []}

    for row in templates:
        part_dict = {"id": row[0], "template": json.loads(row[1])}
        res_dict["templates"].append(part_dict)

    return jsonify(res_dict)


@app.route('/api/teacher/new_category/<teacher_id>', methods=['POST'])
def api_create_category(teacher_id):
    allowed_user = int(teacher_id)
    authorized, message = auth.authorize_teacher(allowed_user)
    if not authorized:
        return jsonify(message), 401

    info = request.json

    name = info['name']

    id_ = models.new_category(teacher_id, name)

    return str(id_), 201


@app.route('/api/teacher/list_categories/<teacher_id>', methods=['GET'])
def api_list_categories(teacher_id):
    allowed_user = int(teacher_id)
    authorized, message = auth.authorize_teacher(allowed_user)
    if not authorized:
        return jsonify(message), 401

    categories = models.all_categories(teacher_id)

    cat_dict = utils.query_to_dict(categories, "categories", [(0, "id"), (1, "name")])

    return jsonify(cat_dict)


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
    allowed_user = int(student_id)
    authorized, message = auth.authorize_student(allowed_user)
    if not authorized:
        return jsonify(message), 401

    experiments = models.get_pending_experiments(student_id)

    exp_dict = utils.query_to_dict(experiments, 'experiments', [(0, 'id'), (1, 'date')])
    return jsonify(exp_dict)


@app.route('/api/student/questionnaire_info/<student_id>/<experiment_id>', methods=['GET'])
def api_questionnaire_details(student_id, experiment_id):
    allowed_user = int(student_id)
    authorized, message = auth.authorize_student(allowed_user)
    if not authorized:
        return jsonify(message), 401

    info, students = models.get_experiment_info(student_id, experiment_id)

    students_dicts = [{'name': s[1], 'id': s[0]} for s in students]

    res_dict = {'info': models.json.loads(info), 'students': students_dicts}

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

    allowed_user = int(student_id)
    authorized, message = auth.authorize_student(allowed_user)
    if not authorized:
        return jsonify(message), 401

    if not models.check_experiment_exists(student_id, experiment_id):
        abort(400, description='Experiment does not exist')

    info = request.json

    student_response = info["responses"]

    models.update_results(student_id, experiment_id, student_response)

    return 'Response submitted', 201


##################
# AUTHENTICATION #
##################

@app.route('/auth/register', methods=['POST'])
def register_user():
    info = request.json
    email, password, name, role = info['email'], info['password'], info['name'], info['role']

    if auth.check_email_exists(email):
        # Make it a proper response?
        return jsonify({"id": -1, "status": "Nope, email taken"}), 401

    if role not in ('teacher', 'student'):
        return jsonify({"id": -1, "status": "Role has to be either teacher or student"}), 401

    pwd_hash = generate_password_hash(password)
    user_id = models.create_user(email, pwd_hash, name, role)

    response = {"id": user_id, "status": "Worked"}
    return jsonify(response)


@app.route('/auth/login', methods=['POST'])
def login_user():
    info = request.json
    email, password = info['email'], info['password']
    # print(email, password)

    info = models.get_user_info(email)
    if len(info) == 0:
        response = {
            "status": "Failure",
            "message": "User does not exist",
        }
        return jsonify(response), 404

    user_id, pwd_hash = info[0]

    # print(user_id, pwd_hash)

    if not check_password_hash(pwd_hash, password):
        response = {
            "status": "Failure",
            "message": "Wrong password"
        }
        return jsonify(response), 404

    token = auth.encode_auth_token(user_id)

    teacher_id, student_id = models.identify_user(user_id)[0]

    response = {
        "status": "Success",
        "message": "Successfully logged in",
        "auth_token": token.decode(),
        "teacher_id": teacher_id,
        "student_id": student_id
    }

    return jsonify(response)


@app.route('/auth/logout', methods=['POST'])
def logout_user():
    auth_token = request.headers.get('Authorization')

    if auth_token is None:
        response = {
            "status": "Failure",
            "message": "Need an Authorization header with the format: Bearer <token>"
        }
        return jsonify(response), 400

    try:
        token = auth_token.split(" ")[1]
    except IndexError:
        response = {
            "status": "Failure",
            "message": "Malformed auth token. Use the format: Bearer <token>"
        }
        return jsonify(response), 400

    user_id = auth.decode_auth_token(token)
    if isinstance(user_id, str):
        response = {
            "status": "Failure",
            "message": "Wrong token"
        }
        return jsonify(response), 400

    models.run_simple_query("INSERT INTO blacklist (token, blacklisted_on) VALUES (?, ?)", (token, time.time()))

    response = {
        "status": "Success",
        "message": "Logged out",
        "user_id": user_id
    }

    return jsonify(response)


@app.route('/auth/test', methods=['GET'])
def test_token():
    auth_token = request.headers.get('Authorization')

    if auth_token is None:
        response = {
            "status": "Failure",
            "message": "Need an Authorization header with the format: Bearer <token>"
        }
        return jsonify(response), 400

    try:
        token = auth_token.split(" ")[1]
    except IndexError:
        response = {
            "status": "Failure",
            "message": "Malformed auth token. Use the format: Bearer <token>"
        }
        return jsonify(response), 400

    user_id = auth.decode_auth_token(token)
    if isinstance(user_id, str):
        response = {
            "status": "Failure",
            "message": "Wrong token: " + user_id
        }
        return jsonify(response), 400

    response = {
        "status": "Success",
        "message": "Logged in",
        "user_id": user_id
    }

    return jsonify(response)


@app.route('/api/teacher/replies_graph/<experiment_id>', methods=['GET'])
def graph_api(experiment_id):
    class_owner = models.run_simple_query("SELECT c.teacher_id FROM classes c "
                                          "JOIN experiments e on c.id = e.class_id WHERE e.id = ?",
                                          (experiment_id,))[0][0]

    allowed_user = int(class_owner)
    authorized, message = auth.authorize_teacher(allowed_user)
    if not authorized:
        return jsonify(message), 401

    questions = models.get_experiment_details(experiment_id)
    questions = json.loads(questions)

    teacher_query = """SELECT c.id, t.name FROM experiments e 
    JOIN classes c on e.class_id = c.id 
    JOIN teachers t on c.teacher_id = t.id
    WHERE e.id = ?"""
    class_id, teacher_name = models.run_simple_query(teacher_query, (experiment_id,))[0]

    replies = models.get_experiment_replies(experiment_id)
    replies = json.loads(replies)

    students = models.get_students_in_class(class_id)
    students = utils.query_to_dict(students, 'nodes', [(0, 'id'), (1, 'label'), (0, 'group')])

    # print(replies)

    response = {'teacher': teacher_name, 'questions': [], 'nodes': students['nodes']}

    for i, question in enumerate(questions['questions']):
        question_dict = {'text': question['text'], 'type': question['type'], 'edges': []}
        # print(question_dict)
        response['questions'].append(question_dict)

        # Bit of spaghetti, but builds the edges array
        for reply_dict in replies['replies']:
            question_reply = reply_dict['response'][i]
            if isinstance(question_reply, list):
                for reply in question_reply:
                    question_dict['edges'].append({'from': reply_dict['id'], 'to': reply})

    return jsonify(response)


"""
{
teacher_name: "
questions: [
    {
    question: ...,
    time: ...,
    nodes: [
        {id: 1, label: "Kata", group: 1, ...},
        {id; 2, ....}
        ],
        
    edges: [
        {from: 1, to: 2},
        {from: 5, to: 3},
        ...
        ]
    },
    {
    nodes: ..., edges: ...
    }
    
"""

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


if __name__ == '__main__':
    app.run(debug=True)
