General note: I'm using the words questionnaire and experiment interchangeably as I'm unable to make up my mind

## Teacher API

**/api/reset**

GET

Resets the database to the original state (for debugging)

The default database contains 200 students with 10 'normal' classes,
each containing students 1-20, 21-40 etc.

Teacher 1 owns classes 1, 2; Teacher 2 owns classes 3, 4; etc.

There's also 5 'special' classes containing various number of students with nontrivial overlaps.
Each teacher owns one of those.

A single initial experiment is created for class 1 (id), and replies are provided by students 1 and 2.

<br></br>

**/api/teacher/get_classes/<teacher_id>**

GET

Returns a list of classes belonging to the selected teacher

```
{
  "classes": [
    {
      "description": "Praesent lectus. Vestibulum quam sapien, varius ut, blandit non, interdum in, ante.", 
      "id": 1, 
      "name": "9Y"
    }, 
    {
      "description": "Proin leo odio, porttitor id, consequat in, consequat ut, nulla. Sed accumsan felis.", 
      "id": 2, 
      "name": "9Q"
    }, 
    {
      "description": "Donec quis orci eget orci vehicula condimentum.", 
      "id": 11, 
      "name": "SPEC4M"
    }
  ]
}
```

<br></br>

**/api/teacher/get_students/<class_id>**

GET

Returns a list of students belonging to the selected class

```
{
  "students": [
    {
      "id": 1, 
      "name": "Garvy Haddleston"
    }, 
    {
      "id": 2, 
      "name": "Riobard Stennet"
    }, 
    {
      "id": 3, 
      "name": "Herculie Gartside"
    },
    ...
  ]
}
```

**/api/teacher/get_experiments/<class_id>**

GET

Returns a list of all experiments pushed to the chosen class

```
{
  "experiments": [
    {
      "date_created": 1556887997.522785, 
      "finished": 0, 
      "id": 1, 
      "info": {
        "questions": [
          {
            "max": 3, 
            "min": 0, 
            "question_no": 0, 
            "text": "Socio1", 
            "type": "sociometric"
          }, 
          {
            "max": 3, 
            "min": 1, 
            "question_no": 1, 
            "text": "Scalar2", 
            "type": "scalar"
          }, 
          {
            "max": 1, 
            "min": 1, 
            "question_no": 2, 
            "text": "Socio3", 
            "type": "sociometric"
          }
        ]
      }, 
    "replies": [
            {
              "id": 1, 
              "response": [
                [], 
                2, 
                [6]
              ]
            }, 
            {
              "id": 2, 
              "response": [
                [1, 6, 7], 
                3, 
                [1]
              ]
            }
      ]
    }
  ]
}
```

The API endpoint above has been split into three parts: 

**/api/teacher/list_experiments/<class_id>**

**/api/teacher/experiment_details/<experiment_id>**

**/api/teacher/experiment_replies**

They all do more or less what you expect them to do - the first one sends a list of (id, date) info for each experiment,
the second one gives you questions and info like that, and the third one gives you replies given by the students.
Figuring out the exact format shall be left as an exercise for the reader.

<br></br>

**/api/teacher/create_experiment/<class_id>/<student_id>**

POST

Creates an experiment (questionnaire) and sends it to the chosen classroom. 
The information about the experiment should be contained in a JSON in the body of the request, like such:

```json
{
  "questions": ["Socio1", "Scalar2", "Socio3"],
  "mins": [0, 1, 1],
  "maxs": [3, 3, 3],
  "type": ["sociometric", "scalar", "sociometric"]
}
```

Each array needs to be of the same length, with the i-th question described by the i-th position of each array


## Student API

**/api/student/get_questionnaires/<student_id>**

GET

Returns a list of experiments pending for the selected student

```json
{
  "experiments": [
    {
      "date": 1556888553.9775023, 
      "id": 1
    }
  ]
}
```

<br></br>

**/api/student/questionnaire_info/<student_id>/<experiment_id>**

GET

Returns information about the questionnaire, 
as well as a list of students in the appropriate class (excluding the student who's responding)

```
{
  "info": {
    "questions": [
      {
        "max": 3, 
        "min": 0, 
        "question_no": 0, 
        "text": "Socio1", 
        "type": "sociometric"
      }, 
      {
        "max": 3, 
        "min": 1, 
        "question_no": 1, 
        "text": "Scalar2", 
        "type": "scalar"
      }, 
      {
        "max": 1, 
        "min": 1, 
        "question_no": 2, 
        "text": "Socio3", 
        "type": "sociometric"
      }
    ]
  }, 
  "students": [
    {
      "id": 1, 
      "name": "Garvy Haddleston"
    }, 
    {
      "id": 2, 
      "name": "Riobard Stennet"
    },
    ...
  ]
}
```

<br></br>

**/api/student/questionnaire_reply/<student_id>/<experiment_id>**

POST

Sends a response for the chosen student, to the chosen questionnaire.
The response should be formatted as follows:

```json
{"responses":
    [
      [1, 6, 7], 
      3, 
      [1]
    ]
}
```
In this case, the student chose classmates with id's 1, 6, 7 as a response to the first question (which is sociometric).
They also chose 3 as the response to the second question, which is a scale question.
Finally they chose one student with id 1 as a response to the third (sociometric) question.