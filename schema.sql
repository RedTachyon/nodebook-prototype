DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS classes;
DROP TABLE IF EXISTS classes_students;
DROP TABLE IF EXISTS experiments;
DROP TABLE IF EXISTS teachers;
DROP TABLE IF EXISTS questionnaires;
DROP TABLE IF EXISTS templates;
DROP TABLE IF EXISTS experiments_students;
DROP TABLE IF EXISTS template_categories;
DROP TABLE IF EXISTS blacklist;


CREATE TABLE IF NOT EXISTS `users`
(
    `id` INTEGER PRIMARY KEY AUTOINCREMENT ,
    `email` TEXT,
    `password` TEXT,
    `student_id` INTEGER,
    `teacher_id` INTEGER,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (teacher_id) REFERENCES teachers(id)
);

CREATE TABLE IF NOT EXISTS `blacklist`
(
    `id` INTEGER PRIMARY KEY AUTOINCREMENT ,
    `token` TEXT,
    `blacklisted_on` date
);

CREATE TABLE IF NOT EXISTS `students`
(
    `id`   INTEGER PRIMARY KEY AUTOINCREMENT,
    `name` TEXT
--     `user_id` INTEGER,
--     FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS `teachers`
(
    `id`   INTEGER PRIMARY KEY AUTOINCREMENT,
    `name` TEXT
--     `user_id` INTEGER,
--     FOREIGN KEY (user_id) REFERENCES users (id)
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

CREATE TABLE IF NOT EXISTS `template_categories`
(
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `name` TEXT,
    `teacher_id` INTEGER,
    FOREIGN KEY (teacher_id) REFERENCES teachers (id)
);

CREATE TABLE IF NOT EXISTS templates
(
    `id`         INTEGER PRIMARY KEY AUTOINCREMENT,
    `content`    json,
    `category_id` INTEGER,
    FOREIGN KEY (category_id) REFERENCES template_categories (id)
--     `teacher_id` INTEGER,
--     FOREIGN KEY (teacher_id) REFERENCES teachers (id)
);

