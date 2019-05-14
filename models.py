import sqlite3 as sql
from os import path
import time
import json
from werkzeug.security import generate_password_hash

ROOT = path.dirname(path.relpath(__file__))
DB_PATH = path.join(ROOT, 'nodedata.db')


def run_simple_query(query, args):
    con = sql.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(query, args)
    result = cur.fetchall()
    con.commit()
    con.close()

    return result


def initialize():
    con = sql.connect(DB_PATH)
    cur = con.cursor()

    with open(path.join(ROOT, 'schema.sql')) as f:
        script = f.read()
        cur.executescript(script)

    con.close()


def seed_data(filename):
    con = sql.connect(DB_PATH)
    cur = con.cursor()

    with open(path.join(ROOT, filename)) as f:
        script = f.read()
        cur.executescript(script)

    con.close()

    create_test_users()



def create_test_users():
    """
    Creates users for testing authentication.
    """
    insert_list = []
    students = get_all_students()
    teachers = get_all_teachers()

    # I'm aware this is very unsafe - only to be used to generate fake data from a predefined set of users.
    for (id_, name) in students:
        pwd_hash = generate_password_hash(str(id_))
        insert_list.append(f"INSERT INTO users (email, password, student_id) "
                           f"VALUES ('{name}', '{pwd_hash}', '{id_}');")

    for (id_, name) in teachers:
        pwd_hash = generate_password_hash(str(id_))
        insert_list.append(f"INSERT INTO users (email, password, teacher_id) "
                           f"VALUES ('{name}', '{pwd_hash}', '{id_}');")

    script = '\n'.join(insert_list)

    # print(script)

    con = sql.connect(DB_PATH)
    cur = con.cursor()
    cur.executescript(script)

    con.close()


def create_teacher(name):
    con = sql.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("INSERT INTO teachers (name) VALUES (?)", (name,))
    con.commit()
    con.close()


def create_class(name, teacher_id, description):
    con = sql.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("INSERT INTO classes (name, teacher_id, description) VALUES (?, ?, ?)", (name, teacher_id, description))

    class_id = cur.lastrowid

    con.commit()
    con.close()

    return class_id


def get_students_in_class(class_id):
    con = sql.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""SELECT s.id, s.name FROM students s
                    LEFT OUTER JOIN classes_students cs ON s.id = cs.student_id
                    WHERE cs.class_id = ?""", (class_id,))
    students = cur.fetchall()
    con.close()
    return students


def get_all_students():
    con = sql.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""SELECT id, name FROM students""")
    students = cur.fetchall()
    con.close()
    return students


def get_all_teachers():
    con = sql.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""SELECT id, name FROM teachers""")
    students = cur.fetchall()
    con.close()
    return students


def generate_result_json(questions, mins, maxs, types):
    output = {'questions': []}

    for i, (question, min_ans, max_ans, type_) in enumerate(zip(questions, mins, maxs, types)):
        question_info = {'text': question,
                         'min': min_ans,
                         'max': max_ans,
                         'question_no': i,
                         'type': type_}

        output['questions'].append(question_info)

    json_string = json.dumps(output)
    return json_string


def create_questionnaire(questions, mins, maxs, class_id, types):
    # if type_ not in ('sociometric', 'scale'):
    #     return -1

    con = sql.connect(DB_PATH)
    cur = con.cursor()

    timestamp = time.time()
    results = generate_result_json(questions, mins, maxs, types)

    # Create experiment entry
    cur.execute("INSERT INTO experiments (info, replies, class_id, date_created, finished) "
                "VALUES (?, ?, ?, ?, ?)",
                (results, '{"replies": []}', class_id, timestamp, 0))

    experiment_id = cur.lastrowid

    con.commit()
    con.close()

    return experiment_id


def push_questionnaire(experiment_id, class_id):
    students = get_students_in_class(class_id)  # id, name

    con = sql.connect(DB_PATH)
    cur = con.cursor()

    for (student_id, _) in students:
        cur.execute("INSERT INTO experiments_students (experiment_id, student_id) VALUES (?, ?)",
                    (experiment_id, student_id))

    con.commit()
    con.close()


def get_classes(teacher_id):
    con = sql.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""SELECT id, name, teacher_id, description FROM classes
                    WHERE teacher_id = ?""", (teacher_id,))
    classes = cur.fetchall()
    con.close()
    return classes


def get_teachers():
    con = sql.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT * FROM teachers")
    teachers = cur.fetchall()
    con.close()
    return teachers


def get_experiments(class_id):
    con = sql.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""SELECT id, info, replies, class_id, date_created, finished FROM experiments
                    WHERE class_id = ?""", (class_id,))
    experiments = cur.fetchall()
    con.close()
    return experiments


def list_experiments(class_id):
    con = sql.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("SELECT id, date_created FROM experiments WHERE class_id=?", (class_id,))

    experiments = cur.fetchall()
    con.close()
    return experiments


def get_experiment_details(experiment_id):
    con = sql.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("SELECT info FROM experiments WHERE id = ?", (experiment_id,))

    info = cur.fetchall()[0][0]
    con.close()
    return info


def get_teacher_experiment_replies(experiment_id):
    con = sql.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("SELECT replies FROM experiments WHERE id = ?", (experiment_id,))

    replies = cur.fetchall()[0][0]
    con.close()
    return replies


def get_pending_experiments(student_id):
    con = sql.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""SELECT e.id, e.date_created, e.class_id
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
    con = sql.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("""SELECT info, class_id FROM experiments
                    WHERE id = ?
                    """, (experiment_id,))

    info, class_id = cur.fetchall()[0]
    # print(info)

    # Get all other students in class
    cur.execute("""SELECT s.id, s.name FROM students s
                    LEFT OUTER JOIN classes_students cs on s.id = cs.student_id
                    WHERE cs.class_id = ? and s.id != ?
                    """, (class_id, student_id))

    students = cur.fetchall()
    con.close()
    return info, students


def get_experiment_replies(experiment_id):
    con = sql.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("SELECT replies FROM experiments WHERE id = ?", (experiment_id,))
    replies = cur.fetchall()

    con.close()

    return replies[0][0]


def update_results(student_id, experiment_id, student_response):
    """
    student_response should be like
    [ [3, 5], 2, [7], [] ]
    If questions 0, 2, 3 were sociometric and question 1 was scale

    """

    replies = get_experiment_replies(experiment_id)
    replies_dict = json.loads(replies)

    replies_dict['replies'].append({"id": int(student_id), "response": student_response})

    new_replies = json.dumps(replies_dict)

    con = sql.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("UPDATE experiments SET replies = ? WHERE id = ?", (new_replies, experiment_id))

    cur.execute("DELETE FROM experiments_students "
                "WHERE student_id = ? AND experiment_id = ?", (student_id, experiment_id))

    con.commit()

    con.close()


def check_experiment_exists(student_id, experiment_id):
    con = sql.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("SELECT * FROM experiments_students WHERE student_id = ? AND experiment_id = ?",
                (student_id, experiment_id))

    response = cur.fetchall()

    con.close()

    if len(response) > 0:
        return True
    else:
        return False


def save_template(category_id, content):
    con = sql.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("INSERT INTO templates (content, category_id) VALUES (?, ?)", (content, category_id))

    con.commit()
    con.close()


def load_templates(category_id):
    con = sql.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("SELECT id, content FROM templates WHERE category_id = ?", (category_id,))

    templates = cur.fetchall()

    con.commit()
    con.close()

    return templates


def new_category(teacher_id, name):
    con = sql.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("INSERT INTO template_categories (name, teacher_id) VALUES (?, ?)", (name, teacher_id))
    id_ = cur.lastrowid

    con.commit()
    con.close()

    return id_


def all_categories(teacher_id):
    con = sql.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("SELECT id, name FROM template_categories WHERE teacher_id = ?", (teacher_id,))

    categories = cur.fetchall()

    con.commit()
    con.close()

    return categories


def create_user(email, password_hash, name, role):
    if role not in ('teacher', 'student'):
        return -1

    con = sql.connect(DB_PATH)
    cur = con.cursor()

    if role == "teacher":
        cur.execute("INSERT INTO teachers (name) VALUES (?)", (name,))
        teacher_id = cur.lastrowid
        student_id = None

    elif role == "student":
        cur.execute("INSERT INTO students (name) VALUES (?)", (name,))
        student_id = cur.lastrowid
        teacher_id = None

    else:
        student_id = teacher_id = None

    cur.execute("INSERT INTO users (email, password, student_id, teacher_id) VALUES (?, ?, ?, ?)",
                (email, password_hash, student_id, teacher_id))

    id_ = cur.lastrowid

    con.commit()
    con.close()

    return id_


def get_user_info(email):
    con = sql.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("SELECT id, password FROM users WHERE email = ?", (email,))
    pwd = cur.fetchall()

    con.close()

    return pwd


def teacher_user_id(teacher_id):
    con = sql.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("SELECT id FROM users WHERE teacher_id = ?", (teacher_id,))
    id_ = cur.fetchall()

    con.close()

    return id_


def student_user_id(student_id):
    con = sql.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("SELECT id FROM users WHERE student_id = ?", (student_id,))
    id_ = cur.fetchall()

    con.close()

    return id_


def identify_user(user_id):
    con = sql.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("SELECT teacher_id, student_id FROM users WHERE id = ?", (user_id,))
    id_ = cur.fetchall()

    con.close()

    return id_

