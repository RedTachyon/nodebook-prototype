import requests
import threading
import datetime
import random
import json

URL = "https://redtachyon.eu.pythonanywhere.com"
TEACHER_TOKEN = 'SKELETON_KEY'



def reset():
    url = URL + '/demo/reset'

    res = requests.get(url, headers={'Authorization': TEACHER_TOKEN})
    return res


def submit_response(student_id, responses):
    url = URL + f'/api/student/questionnaire_reply/{student_id}/1'

    # data = {
    #     "responses": [
    #         [random.choice(range(1, 58))],
    #         [random.choice(range(1, 58)), random.choice(range(1, 58)), random.choice(range(1, 58))]
    #     ]
    # }

    data = {
        "responses": responses,
    }

    headers = {"Authorization": "SKELETON_KEY"}

    res = requests.post(url, headers=headers, json=data)
    return res


def create_questionnaire():
    url = URL + '/api/teacher/create_experiment/1'
    data = {
        "questions": ["Who would you like to work with on your next project?"],
        "mins": [0],
        "maxs": [2],
        "type": ["sociometric"]
    }

    headers = {"Authorization": "SKELETON_KEY"}

    res = requests.post(url, headers=headers, json=data)
    return res


def register_login(username='auto', name='auto', password='auto'):
    url = URL + '/demo/register'
    data = {
        "email": username,
        "name": name,
        "password": password,
        "role": "student"
    }
    res = requests.post(url, json=data)

    return res


def backup_more_users(n=15):
    names = [
        'Rhaegar',
        'Aegon',
        'Jon',
        'Dany',
        'Ramsay',
        'Theon',
        'Euron',
        'Yara',
        'Ned',
        'Arya',
        'Sansa',
        'Sam',
        'Gilly',
        'Podrick',
        'Brienne'
    ]
    ids = []
    for i in range(n):
        name = names[i]
        res = register_login(name, name, name)
        res = json.loads(res.content)
        ids.append(int(res['student_id']))

    last_id = ids[-1]
    return ids


def backup_replies(ids):
    last_id = ids[-1]
    for id_ in ids:
        submit_response(id_, [[random.choice(range(3, last_id)), random.choice(range(3, last_id))]])


def submit_ours():
    submit_response(1, [[2]])
    submit_response(2, [[4]])
    submit_response(3, [[2]])
    submit_response(4, [[1]])
    submit_response(5, [[4]])
    submit_response(6, [[7]])
    submit_response(7, [[6]])
