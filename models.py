import sqlite3 as sql
from os import path
import time
import json

ROOT = path.dirname(path.relpath(__file__))


def create_teacher(name):
    con = sql.connect(path.join(ROOT, 'nodedata.db'))
    cur = con.cursor()
    cur.execute("INSERT INTO teachers (name) VALUES (?)", (name,))
    con.commit()
    con.close()


def create_class(name, teacher_id, description):
    con = sql.connect(path.join(ROOT, 'nodedata.db'))
    cur = con.cursor()
    cur.execute("INSERT INTO classes (name, teacher_id, description) VALUES (?, ?, ?)", (name, teacher_id, description))
    con.commit()
    con.close()


def generate_result_json(questions, mins, maxs):

    output = {'questions': []}

    for i, (question, min_ans, max_ans) in enumerate(zip(questions, mins, maxs)):
        question_info = {'text': question,
                         'min': min_ans,
                         'max': max_ans,
                         'question_no': i}

        output['questions'].append(question_info)

    json_string = json.dumps(output)
    return json_string


def create_questionnaire(questions, mins, maxs, class_id):
    con = sql.connect(path.join(ROOT, 'nodedata.db'))
    cur = con.cursor()

    timestamp = time.time()
    results = generate_result_json(questions, mins, maxs)

    # Create experiment entry
    cur.execute("INSERT INTO experiments (info, replies, class_id, date_created, finished) VALUES (?, ?, ?, ?, ?)",
                (results, '{"replies": []}', class_id, timestamp, 0))

    experiment_id = cur.lastrowid

    con.commit()
    con.close()

    return experiment_id


def push_questionnaire(experiment_id, class_id):

    students = get_students_in_class(class_id)  # id, name, class

    con = sql.connect(path.join(ROOT, 'nodedata.db'))
    cur = con.cursor()

    for (student_id, _, _) in students:
        cur.execute("INSERT INTO experiments_students (experiment_id, student_id) VALUES (?, ?)",
                    (experiment_id, student_id))

    con.commit()
    con.close()


def get_classes(teacher_id):
    con = sql.connect(path.join(ROOT, 'nodedata.db'))
    cur = con.cursor()
    cur.execute("""SELECT id, name, teacher_id, description FROM classes
                    WHERE teacher_id = ?""", (teacher_id,))
    classes = cur.fetchall()
    con.close()
    return classes


def get_teachers():
    con = sql.connect(path.join(ROOT, 'nodedata.db'))
    cur = con.cursor()
    cur.execute("SELECT * FROM teachers")
    teachers = cur.fetchall()
    con.close()
    return teachers


def get_experiments(class_id):
    con = sql.connect(path.join(ROOT, 'nodedata.db'))
    cur = con.cursor()
    cur.execute("""SELECT id, info, replies, class_id, date_created, finished FROM experiments
                    WHERE class_id = ?""", (class_id,))
    experiments = cur.fetchall()
    con.close()
    return experiments


def get_students_in_class(class_id):
    con = sql.connect(path.join(ROOT, 'nodedata.db'))
    cur = con.cursor()
    cur.execute("""SELECT students.id, students.name, students.class_id FROM students
                    WHERE class_id = ?""", (class_id,))
    students = cur.fetchall()
    con.close()
    return students


def get_all_students():
    con = sql.connect(path.join(ROOT, 'nodedata.db'))
    cur = con.cursor()
    cur.execute("""SELECT students.id, students.name, classes.name 
                    FROM students
                    LEFT OUTER JOIN classes
                    ON classes.id=students.class_id
                    ORDER BY classes.id
                    """)
    students = cur.fetchall()
    con.close()
    return students


def get_pending_experiments(student_id):
    con = sql.connect(path.join(ROOT, 'nodedata.db'))
    cur = con.cursor()
    cur.execute("""SELECT e.id, e.date_created
                    FROM experiments e
                    LEFT OUTER JOIN experiments_students es 
                    ON e.id = es.experiment_id
                    LEFT OUTER JOIN students s 
                    ON es.student_id = s.id
                    WHERE s.id = ?
                    """, (student_id,))

    experiments = cur.fetchall()
    con.close()
    return experiments


def get_experiment_info(student_id, experiment_id):
    con = sql.connect(path.join(ROOT, 'nodedata.db'))
    cur = con.cursor()

    cur.execute("""SELECT info FROM experiments
                    WHERE id = ?
                    """, experiment_id)

    info = cur.fetchall()

    cur.execute("""SELECT id, name FROM students
                    WHERE id != ? AND class_id IN 
                        (SELECT class_id FROM students WHERE id = ?)
                    """, (student_id, student_id))

    students = cur.fetchall()
    con.close()
    return info, students


def get_experiment_replies(experiment_id):
    con = sql.connect(path.join(ROOT, 'nodedata.db'))
    cur = con.cursor()

    cur.execute("SELECT replies FROM experiments WHERE id=?", (experiment_id,))
    replies = cur.fetchall()

    con.close()

    return replies[0][0]


def update_results(student_id, experiment_id, students_chosen):

    replies = get_experiment_replies(experiment_id)
    replies_dict = json.loads(replies)

    replies_dict['replies'].append({student_id: students_chosen})

    new_replies = json.dumps(replies_dict)

    con = sql.connect(path.join(ROOT, 'nodedata.db'))
    cur = con.cursor()

    cur.execute("UPDATE experiments SET replies = ? WHERE id = ?", (new_replies, experiment_id))

    cur.execute("DELETE FROM experiments_students "
                "WHERE student_id = ? AND experiment_id = ?", (student_id, experiment_id))

    con.commit()

    con.close()


def check_experiment_exists(student_id, experiment_id):
    con = sql.connect(path.join(ROOT, 'nodedata.db'))
    cur = con.cursor()

    cur.execute("SELECT * FROM experiments_students WHERE student_id = ? AND experiment_id = ?",
                (student_id, experiment_id))

    response = cur.fetchall()

    if len(response) > 0:
        return True
    else:
        return False
