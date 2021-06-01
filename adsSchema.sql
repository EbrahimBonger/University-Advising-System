SET GLOBAL sql_mode = (SELECT REPLACE (@@sql_mode, 'ONLY_FULL_GROUP_BY',''));
SET FOREIGN_KEY_CHECKS=0;
                                       
DROP TABLE IF EXISTS prerequisites;
DROP TABLE IF EXISTS transcript;
DROP TABLE IF EXISTS courseSchedule;
DROP TABLE IF EXISTS courseCatalog;
DROP TABLE IF EXISTS formOne;
DROP TABLE IF EXISTS appList;
DROP TABLE IF EXISTS recInfo;
DROP TABLE IF EXISTS applicantInfo;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS alumni;
DROP TABLE IF EXISTS suspended;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS reviewInfo;
DROP TABLE IF EXISTS degreeInfo;

CREATE TABLE users (
    UID int(8) AUTO_INCREMENT NOT NULL,
    email varchar(100) NOT NULL,
    passw varchar(100) NOT NULL,
    fname varchar(20),
    lname varchar(30),
    address varchar(100),
    SSN bigint(9),
    phone bigint(10),
    primary key (UID)  
) AUTO_INCREMENT = 10000000;
                                       
-- 0 app, 1 student, 2 alumni, 3 faculty, 4 GS, 5 Admin, 6 CAC, 7 suspended student
CREATE TABLE roles (
    UID int(8) NOT NULL,
    roleID int(1) NOT NULL,
    primary key (UID, roleID),
    foreign key (UID) references users (UID)
);

CREATE TABLE student (
    UID int(8) NOT NULL,
    major varchar(50),
    school varchar(30),
    program varchar(10),
    degree varchar(7),
    admissionSemester varchar(6),
    interests varchar(200),
    priorWork varchar(200),
    yearObtained year,
    advisorUID int(8) NOT NULL,
    primary key(UID),
    foreign key (UID) references users (UID),
    foreign key (advisorUID) references users (UID)
);
                                       
CREATE TABLE alumni (
    UID int(8) NOT NULL,
    yearObtained year,
    primary key(UID),
    foreign key (UID) references student (UID)
);



CREATE TABLE applicantInfo (
    UID int(8) NOT NULL,
    submitted timestamp,
    app_reviewed boolean, 
    decision_made boolean,
    decision varchar(25),
    app_accepted boolean,
    transcript boolean, 
    transcript_path varchar(255),
    recommendations boolean,
    degreeSought varchar(7),
    admissionSemester varchar(6),
    priorWork varchar(200),
    interests varchar(200),
    GREverbal int(3),
    GREquant int(3),
    program varchar(40),
    advisor int(8),
    primary key (UID),
    foreign key (UID) references users (UID)
);
                                       
CREATE TABLE degreeInfo (
    UID int(8),
    type varchar(10),
    major varchar(50),
    school varchar(30),
    GPA float(3,2),
    yearObtained year,

    primary key (UID,yearObtained),
    foreign key (UID) references applicantInfo (UID)
);                                       

CREATE TABLE recInfo (
    UID int(8) NOT NULL,
    recFname varchar(20),
    recLname varchar(30),
    email varchar(30),
    affiliation varchar(30),
    title varchar(20),
    submitted timestamp,
    content varchar(255),
    primary key (UID,email),
    foreign key (UID) references applicantInfo (UID)
);
                                       
CREATE TABLE reviewInfo (
    UID int(8),
    reviewerUID int(8),
    recommendation int(1),
    letterrating varchar(1),
    comments varchar(200),
    reviewed timestamp,

    primary key (UID, reviewerUID),
    foreign key (UID) references applicantInfo (UID)
);                                       


CREATE TABLE appList (
    UID int(8) NOT NULL, 
    advisorUID int(8) NOT NULL,
    status varchar(50) NOT NULL,
    primary key (UID),
    foreign key (UID) references student (UID)
);


CREATE TABLE formOne (
    UID int(8) NOT NULL,
    dept varchar(50), 
    courseNum int(4) NOT NULL,
    credits int(1),
    grade varchar(2),
    semester varchar(7),
    foreign key (UID) references student (UID)
);

CREATE TABLE courseCatalog (
    catalogID int NOT NULL,
    department varchar(5) NOT NULL,
    courseNum int(4) NOT NULL,
    title varchar(25),
    credits int(1),
    description varchar(350),
    primary key (catalogID)
);

CREATE TABLE courseSchedule (
    courseID int NOT NULL,
    catalogID int NOT NULL,
    courseDay varchar(1), 
    courseTimeStart time,
    courseTimeStop time,
    facultyUID int(8),
    semester varchar(7),
    academicYear int(4),
    seatCapacityLive int(3),
    seatCapacityStatic int (3),
    building varchar (50),
    primary key (courseID),
    foreign key (facultyUID) references users (UID),
    foreign key (catalogID) references courseCatalog (catalogID) 
);

CREATE TABLE transcript (
    UID int (8) NOT NULL,
    transcriptID int AUTO_INCREMENT,
    courseID int NOT NULL,
    grade varchar (2),
    transSemester varchar(7),
    transAcademicYear int (4),
    primary key (transcriptID, UID),
    foreign key (UID) references student (UID),
    foreign key (courseID) references courseSchedule (courseID)
) AUTO_INCREMENT = 1;


CREATE TABLE prerequisites (
    catalogID int NOT NULL,
    prereq int NOT NULL,
    primary key (catalogID, prereq),
    foreign key (catalogID) references courseCatalog (catalogID),
    foreign key (prereq) references courseCatalog (catalogID)
);
                                       
SET FOREIGN_KEY_CHECKS=1;

-- Hashed passw: $pbkdf2-sha256$29000$OMe4935v7f2fM8a4FwJgzA$UzK3v.Q3aCYQ0m0I6Q9jjTXgNO001pAB7AtKVs361z4


INSERT INTO `users` (`email`, `passw`, `fname`, `lname`, `address`, `SSN`, `phone`) VALUES ("paul@email.edu", "pass", "Paul", "McCartney", "address", 000000000, 0000000000);


INSERT INTO `users` (`email`, `passw`, `fname`, `lname`, `address`, `SSN`, `phone`) VALUES ("george@email.edu", "pass", "George", "Harrison", "address", 000000000, 0000000000);


INSERT INTO `users` (`email`, `passw`, `fname`, `lname`, `address`, `SSN`, `phone`) VALUES ("eric@email.edu", "pass", "Eric", "Clapton", "address", 000000000, 0000000000);

INSERT INTO `users` (`email`, `passw`, `fname`, `lname`, `address`, `SSN`, `phone`) VALUES ("alex@email.edu", "pass", "Alex", " ", "address", 000000000, 0000000000);

INSERT INTO `users` (`email`, `passw`, `fname`, `lname`, `address`, `SSN`, `phone`) VALUES ("parmer@email.edu", "pass", "Parmer", "Parmer", "address", 000000000, 0000000000);

INSERT INTO `users` (`email`, `passw`, `fname`, `lname`, `address`, `SSN`, `phone`) VALUES ("john@email.edu", "pass", "john", "Smith", "address", 000000000, 0000000000);






INSERT INTO `roles` (`UID`, `roleID`) VALUES (10000000, 1);
INSERT INTO `roles` (`UID`, `roleID`) VALUES (10000001, 1);
INSERT INTO `roles` (`UID`, `roleID`) VALUES (10000002, 1);
INSERT INTO `roles` (`UID`, `roleID`) VALUES (10000003, 3);
INSERT INTO `roles` (`UID`, `roleID`) VALUES (10000004, 3);
INSERT INTO `roles` (`UID`, `roleID`) VALUES (10000005, 4);



INSERT INTO `student` (`UID`, `major`, `school`, `program`, `degree`, `admissionSemester`, `interests`, `priorWork`, `yearObtained`, `advisorUID`) VALUES (10000000, "Computer Science", "seas", "Masters", "BS", "Fall18", "coding", "priorWork", 2022, 10000003);

INSERT INTO `student` (`UID`, `major`, `school`, `program`, `degree`, `admissionSemester`, `interests`, `priorWork`, `yearObtained`, `advisorUID`) VALUES (10000001, "Computer Science", "seas", "PHD", "BS", "Fall18", "coding", "priorWork", 2022, 10000004);

INSERT INTO `student` (`UID`, `major`, `school`, `program`, `degree`, `admissionSemester`, `interests`, `priorWork`, `yearObtained`, `advisorUID`) VALUES (10000002, "Computer Science", "seas", "Masters", "BS", "Fall18", "coding", "priorWork", 2022, 10000004);


INSERT INTO `alumni` VALUES (10000002, 2021);





INSERT INTO courseCatalog  VALUES (1, "CSCI", 6221, "SW Paradigms", 3, "Review of programming in a high-level language using Java or C++ Introduction to objects and object-oriented programming: static and dynamic objects, inheritance, dynamic method invocation. Data structures: 2D-arrays, linked-lists, stacks, queues, trees, hashing");
INSERT INTO courseCatalog  VALUES (2, "CSCI", 6461, "Computer Architecture", 3, "Concepts in processor, system, and network architectures; architecture of pipeline, superscalar, and VLIW/EPIC processors; multiprocessors and interconnection networks; cache coherence and memory subsystem design for multiprocessor architectures; parallel and distributed system architecture; internetworking.");
INSERT INTO courseCatalog  VALUES (3, "CSCI", 6212, "Algorithms", 3, "Structures in continuous mathematics from a computational viewpoint; continuous system simulation, computational modeling, probability, statistical techniques, next-event simulation, algorithms for continuous optimization, machine learning, neural networks, statistical language processing, robot control algorithms.");
INSERT INTO courseCatalog  VALUES (4, "CSCI", 6220, "Machine Learning", 3, "verview of core machine learning techniques: nearest-neighbor, regression, classification, perceptron, kernel methods, support vector machine (SVM), logistic regression, ensemble methods, hidden Markov models (HMM), non-parametrics, online learning, active learning, clustering, feature selection, parameter tuning, and cross-validation.");
INSERT INTO courseCatalog  VALUES (5, "CSCI", 6232, "Networks 1", 3, "Higher-layer protocols and network applications on the Internet, such as session layer, presentation layer, data encryption, directory services and reliable transfer services, telnet, network management, network measurements, e-mail systems, and error reporting.");
INSERT INTO courseCatalog  VALUES (6, "CSCI", 6233, "Networks 2", 3, "Computer networks and open system standards. Network configurations and signals, encoding and modulation, transmission media, connection interfaces, error detection and correction, signal compression, switching, link layer control, ISDN, X.25, frame relay, ATM, and Sonet. Bridges, routers, and routing algorithms.");
INSERT INTO courseCatalog  VALUES (7, "CSCI", 6241, "Database 1", 3, "Design of relational database systems, relational query languages, Introduction to Not just SQL (NoSQL) database systems, normal forms, and design of database applications. ");
INSERT INTO courseCatalog  VALUES (8, "CSCI", 6242, "Database 2", 3, "Concepts in database systems. Relational database design. Editing, report generation, updating, schema refinement, tuning. Construction of database management systems. Conceptual and logical design of a database. ");
INSERT INTO courseCatalog  VALUES (9, "CSCI", 6246, "Compilers", 3, "Concepts underlying all computer systems. Processor operation, hierarchical memory systems, embedded boards, data acquisition, actuation, and systems software such as compilers, linkers, and operating systems from the programmer’s perspective. Use of embedded platforms to examine how programs interact with and are constrained by hardware.");
INSERT INTO courseCatalog  VALUES (10, "CSCI", 6260, "Multimedia", 3, "History, theory, and development of multimedia concepts. Hardware components, platforms, and authoring tools. Scientific, technical, and cognitive foundations of various media including text, sound, graphics, and video. Interface design. Use of a media taxonomy as a design and evaluation tool.");
INSERT INTO courseCatalog  VALUES (11, "CSCI", 6251, "Cloud Computing", 3, "Algorithmic and implementation challenges in building large scale distributed applications; distributed coordination, scheduling, consistency issues, and fault tolerance algorithms; fundamental distributed systems concepts applied to both high performance computing and cloud computing environments.");
INSERT INTO courseCatalog  VALUES (12, "CSCI", 6254, "SW Engineering", 3, "Programming techniques and software development in one or more programming languages; application development with GUIs, database access, threads, web programming.");
INSERT INTO courseCatalog  VALUES (13, "CSCI", 6262, "Graphics 1", 3, "Introduction to computer graphics without programming; building 3-D geometry and rendering; computer animation; virtual reality and computer games; hands-on projects in modeling, rendering, and animation using commercial software; hands-on projects in photo and video manipulation.");
INSERT INTO courseCatalog  VALUES (14, "CSCI", 6283, "Security 1", 3, "Risk analysis, cryptography, operating system security, identification and authentication systems, database security. ");
INSERT INTO courseCatalog  VALUES (15, "CSCI", 6284, "Cryptography", 3, "Algorithmic principles of cryptography from Julius Caesar to public key cryptography. Key management problems and solutions.");
INSERT INTO courseCatalog  VALUES (16, "CSCI", 6286, "Network Security", 3, "Security protocols and applications in local, global, and wireless networks; IPSec and packet-level communication security systems; network authentication and key-exchange protocols; intrusion detection systems and firewalls; secure network applications; network worms and denial-of-service attacks.");
INSERT INTO courseCatalog  VALUES (17, "CSCI", 6325, "Algorithms 2", 3, "Core concepts in design and analysis of algorithms, data structures, and problem-solving techniques. Hashing, heaps, trees. Graph algorithms, searching, sorting, graph algorithms, dynamic programming, greedy algorithms, divide and conquer, backtracking. Combinatorial optimization techniques. ");
INSERT INTO courseCatalog  VALUES (18, "CSCI", 6339, "Embedded Systems", 3, "Process management, process state, concurrent processing, synchronization, events; operating system structure, the kernel approach, processor scheduling, task switching, monitors, threads; system management, memory management, process loading, communication with peripherals; file systems; socket programming, packets, Internet protocols.");
INSERT INTO courseCatalog  VALUES (19, "CSCI", 6384, "Cryptography 2", 3, "Security for software systems. Theory and practice of designing and implementing secure software. Security in the context of software engineering. Practical experience with building a software system and securing it, with emphasis on correctness and robustness. Requires substantial prior programming experience. ");
INSERT INTO courseCatalog  VALUES (20, "ECE", 6241, "Communication Theory", 3, "the detection of signals, the prediction and filtering of random processes, the design and analysis of communication systems, the analysis of protocols for communication networks, and statistical processing of images.");
INSERT INTO courseCatalog  VALUES (21, "ECE", 6242, "Information Theory", 2, " introduction to the mathematics of information theory, with emphasis on modern non-asymptotic techniques and information spectrum methods. We will also discuss various connections/applications to computer science, statistics, and machine learning.");
INSERT INTO courseCatalog  VALUES (22, "MATH", 6210, "Logic", 2, "This course is an introduction to Logic from a computational perspective. It shows how to encode information in the form of logical sentences; it shows how to reason with information in this form; and it provides an overview of logic technology and its applications - in mathematics, science, engineering, business, law, and so forth.");


INSERT INTO courseSchedule VALUES (1, 1, 'M', '150000', '173000', 10000000, 'Spring', 2021, 20, 20, 'SEAS 1130');
INSERT INTO courseSchedule VALUES (2, 2, 'T', '150000', '173000', 10000001, 'Spring', 2021, 20, 20, 'SEAS 2000');
INSERT INTO courseSchedule VALUES (3, 3, 'W', '150000', '173000', 10000000, 'Spring', 2021, 20, 20, 'SEAS 2000');
INSERT INTO courseSchedule VALUES (4, 5, 'M', '180000', '203000', 10000001, 'Spring', 2021, 20, 20, 'SEAS 3340');
INSERT INTO courseSchedule VALUES (5, 6, 'T', '180000', '203000', 10000000, 'Spring', 2021, 20, 20, 'SEAS 9920');
INSERT INTO courseSchedule VALUES (6, 7, 'W', '180000', '203000', 10000001, 'Spring', 2021, 20, 20, 'SEAS 1500');
INSERT INTO courseSchedule VALUES (7, 8, 'R', '180000', '203000', 10000000, 'Spring', 2021, 20, 20, 'SEAS 7830');
INSERT INTO courseSchedule VALUES (8, 9, 'T', '150000', '173000', 10000001, 'Spring', 2021, 20, 20, 'SEAS 4500');
INSERT INTO courseSchedule VALUES (9, 11,'M', '180000', '203000', 10000000, 'Spring', 2021, 20, 20, 'SEAS 1990');
INSERT INTO courseSchedule VALUES (10,12,'M', '153000', '180000', 10000001, 'Spring', 2021, 20, 20, 'SEAS 5600');
INSERT INTO courseSchedule VALUES (11,10,'R', '180000', '203000', 10000000, 'Spring', 2021, 20, 20, 'SEAS 5500');
INSERT INTO courseSchedule VALUES (12,13,'W', '180000', '203000', 10000001, 'Spring', 2021, 20, 20, 'SEAS 1000');
INSERT INTO courseSchedule VALUES (13,14,'T', '180000', '203000', 10000000, 'Spring', 2021, 20, 20, 'SEAS 2300');
INSERT INTO courseSchedule VALUES (14,15,'M', '180000', '203000', 10000001, 'Spring', 2021, 20, 20, 'SEAS 1990');
INSERT INTO courseSchedule VALUES (15,16,'W', '180000', '203000', 10000000, 'Spring', 2021, 20, 20, 'SEAS 4550');
INSERT INTO courseSchedule VALUES (16,19,'W', '150000', '173000', 10000001, 'Spring', 2021, 20, 20, 'SEAS 5600');
INSERT INTO courseSchedule VALUES (17,20,'M', '180000', '203000', 10000000, 'Spring', 2021, 20, 20, 'SEAS 6000');
INSERT INTO courseSchedule VALUES (18,21,'T', '180000', '203000', 10000001, 'Spring', 2021, 20, 20, 'SEAS 4000');
INSERT INTO courseSchedule VALUES (19,22,'W', '180000', '203000', 10000000, 'Spring', 2021, 20, 20, 'SEAS 1000');
INSERT INTO courseSchedule VALUES (20,18,'R', '160000', '183000', 10000001, 'Spring', 2021, 20, 20, 'SEAS 3430');


INSERT INTO prerequisites VALUES (6,5);
INSERT INTO prerequisites VALUES (8,7);
INSERT INTO prerequisites VALUES (9,2);
INSERT INTO prerequisites VALUES (9,3);
INSERT INTO prerequisites VALUES (11,2);
INSERT INTO prerequisites VALUES (12,1);
INSERT INTO prerequisites VALUES (14,3);
INSERT INTO prerequisites VALUES (15,3);
INSERT INTO prerequisites VALUES (16,14);
INSERT INTO prerequisites VALUES (16,5);
INSERT INTO prerequisites VALUES (17,3);
INSERT INTO prerequisites VALUES (18,2);
INSERT INTO prerequisites VALUES (18,3);
INSERT INTO prerequisites VALUES (19,15);




INSERT INTO `transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000000, 0, 1, 'A', 'Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000000, 0, 2, 'A','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000000, 0, 3, 'A','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000000, 0, 4, 'A','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000000, 0, 5, 'A','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000000, 0, 6, 'A','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000000, 0, 7, 'B','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000000, 0, 8, 'B','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000000, 0, 9, 'A','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000000, 0, 13, 'A','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000000, 0, 14, 'A','Fall', 2020);




INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000001, 0, 1, 'B','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000001, 0, 2, 'A','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000001, 0, 3, 'A','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000001, 0, 5, 'A','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000001, 0, 6, 'A','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000001, 0, 7, 'A','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000001, 0, 8, 'A','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000001, 0, 9, 'B','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000001, 0, 13, 'A','Fall', 2020);


INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000001, 0, 14, 'A','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000001, 0, 15, 'A','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000001, 0, 16, 'A','Fall', 2020);


INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000002, 0, 1, 'B','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000002, 0, 2, 'B','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000002, 0, 3, 'B','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000002, 0, 4, 'B','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000002, 0, 5, 'B','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000002, 0, 6, 'B','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000002, 0, 7, 'B','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000002, 0, 8, 'A','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000002, 0, 9, 'A','Fall', 2020);

INSERT INTO`transcript` (`UID`, `transcriptID`, `courseID`, `grade`, `transSemester`, `transAcademicYear`) VALUES (10000002, 0, 10, 'A','Fall', 2020);

