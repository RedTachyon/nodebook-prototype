from flask import Flask, render_template, request, redirect
import sqlite3 as sql
import datetime
import json

from models import get_classes, get_teachers, get_experiments, create_class, create_questionnaire, get_students_in_class
from models import get_all_students, push_questionnaire, get_pending_experiments, get_experiment_info, update_results

app = Flask(__name__)

# Let's check branching


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
