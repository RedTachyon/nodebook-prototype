import requests
import threading
import datetime
import random

URL = "https://redtachyon.eu.pythonanywhere.com"

i = 1
j = 1

TEACHER_TOKEN = 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1NjYyMDI5MDgsImlhdCI6MTU1ODQyNjkwOCwic3ViIjo4fQ.Y3Nnru756J9Ag7eESzUhacggAurXPUIO-oiEYs3lA4Y'


def reset():
    url = URL + '/demo/reset'

    res = requests.get(url)
    return res


def register_login(username='auto', name='auto', password='auto'):
    url = URL + '/demo/register'
    global i
    i += 1
    data = {
        "email": username + str(i),
        "name": name + str(i),
        "password": password,
        "role": "student"
    }
    res = requests.post(url, json=data)

    return res


def create_questionnaire():
    url = URL + '/api/teacher/create_experiment/1'
    data = {
        "questions": ["Who is your best friend in this class?", "Who would you like to work with on your next project?"],
        "mins": [1, 0],
        "maxs": [1, 3],
        "type": ["sociometric", "sociometric"]
    }

    headers = {"Authorization": "SKELETON_KEY"}

    res = requests.post(url, headers=headers, json=data)
    return res


def submit_response():
    global j
    url = URL + f'/api/student/questionnaire_reply/{j}/1'
    j += 1
    data = {
        "responses": [
            [random.choice(range(1, 58))],
            [random.choice(range(1, 58)), random.choice(range(1, 58)), random.choice(range(1, 58))]
        ]
    }

    headers = {"Authorization": "SKELETON_KEY"}

    res = requests.post(url, headers=headers, json=data)
    return res


reset()
print(datetime.datetime.now(), 'Database reset')

threads = []
register_responses = []
for i in range(50):
    x = threading.Thread(target=register_login)
    threads.append(x)
    x.start()
    # res = register_login()
    # register_responses.append(res)

for i, thread in enumerate(threads):
    thread.join()

print(datetime.datetime.now(), 'Users created')

questionnaire_response = create_questionnaire()

print(datetime.datetime.now(), 'Questionnaire created')

threads = []
reply_responses = []
for i in range(57):
    x = threading.Thread(target=submit_response)
    threads.append(x)
    x.start()
    # res = submit_response()
    # reply_responses.append(res)

for i, thread in enumerate(threads):
    thread.join()

print(datetime.datetime.now(), 'Responses submitted')
