insert into students (id, name) values (1, 'Ariel');
insert into students (id, name) values (2, 'Ruxi');
insert into students (id, name) values (3, 'Kata');
insert into students (id, name) values (4, 'Victoria');
insert into students (id, name) values (5, 'Neža');
insert into students (id, name) values (6, 'Tim');
insert into students (id, name) values (7, 'Talha');
-- TEACHER
insert into teachers (id, name) values (1, 'NodeBook Team');
-- CLASS
insert into classes (id, name, teacher_id, description) values (1, 'BDLab', 1, 'A class for the BDLab demo');
insert into classes_students (class_id, student_id) values (1, 1);
insert into classes_students (class_id, student_id) values (1, 2);
insert into classes_students (class_id, student_id) values (1, 3);
insert into classes_students (class_id, student_id) values (1, 4);
insert into classes_students (class_id, student_id) values (1, 5);
insert into classes_students (class_id, student_id) values (1, 6);
insert into classes_students (class_id, student_id) values (1, 7);
