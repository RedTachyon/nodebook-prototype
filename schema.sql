DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS classes;
DROP TABLE IF EXISTS classes_students;
DROP TABLE IF EXISTS experiments;
DROP TABLE IF EXISTS teachers;
DROP TABLE IF EXISTS questionnaires;
DROP TABLE IF EXISTS custom_questionnaires;
DROP TABLE IF EXISTS experiments_students;

CREATE TABLE IF NOT EXISTS `students`
(
    `id`   INTEGER PRIMARY KEY AUTOINCREMENT,
    `name` TEXT
--   `class_id` INTEGER,
--   FOREIGN KEY (class_id) REFERENCES classes(id)
);

CREATE TABLE IF NOT EXISTS `teachers`
(
    `id`   INTEGER PRIMARY KEY AUTOINCREMENT,
    `name` TEXT
);


CREATE TABLE IF NOT EXISTS `classes`
(
    `id`          INTEGER PRIMARY KEY AUTOINCREMENT,
    `name`        TEXT,
    `teacher_id`  INTEGER,
    `description` TEXT,
    FOREIGN KEY (teacher_id) REFERENCES teachers (id)
);


CREATE TABLE IF NOT EXISTS `classes_students`
(
    `class_id`   INTEGER,
    `student_id` INTEGER,
    FOREIGN KEY (class_id) REFERENCES classes (id),
    FOREIGN KEY (student_id) REFERENCES students (id)
);


CREATE TABLE IF NOT EXISTS `experiments`
(
    `id`           INTEGER PRIMARY KEY AUTOINCREMENT,
    `info`         json,
    `replies`      json,
    `class_id`     INTEGER,
    `date_created` date,
--   `type` TEXT,
    `finished`     bool,
    FOREIGN KEY (class_id) REFERENCES classes (id)
);


-- Junction table of pending questions
CREATE TABLE IF NOT EXISTS `experiments_students`
(
    `experiment_id` INTEGER,
    `student_id`    INTEGER,
    FOREIGN KEY (experiment_id) REFERENCES experiments (id),
    FOREIGN KEY (student_id) REFERENCES students (id)
);

CREATE TABLE IF NOT EXISTS `questionnaires`
(
    `id`      INTEGER PRIMARY KEY AUTOINCREMENT,
    `content` json
);

CREATE TABLE IF NOT EXISTS `custom_questionnaires`
(
    `id`         INTEGER PRIMARY KEY AUTOINCREMENT,
    `content`    json,
    `category_id` INTEGER,
    FOREIGN KEY (category_id) REFERENCES template_categories (id)
--     `teacher_id` INTEGER,
--     FOREIGN KEY (teacher_id) REFERENCES teachers (id)
);

CREATE TABLE IF NOT EXISTS `template_categories`
(
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `name` TEXT,
    `teacher_id` INTEGER,
    FOREIGN KEY (teacher_id) REFERENCES teachers (id)

)