import requests
import threading
import datetime
import random

URL = "https://redtachyon.eu.pythonanywhere.com"
TEACHER_TOKEN = 'SKELETON_KEY'


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
