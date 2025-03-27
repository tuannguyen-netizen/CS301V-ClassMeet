CREATE DATABASE classmeetdatabase;
USE classmeetdatabase;

CREATE TABLE User (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE Class (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    creator_id INT,
    FOREIGN KEY (creator_id) REFERENCES User(id)
);

CREATE TABLE Class_membership (
    class_id INT,
    user_id INT,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    role ENUM('student', 'teacher', 'admin') DEFAULT 'student',
    PRIMARY KEY (class_id, user_id),
    FOREIGN KEY (class_id) REFERENCES Class(id),
    FOREIGN KEY (user_id) REFERENCES User(id)
);

CREATE TABLE Meeting (
    id INT PRIMARY KEY AUTO_INCREMENT,
    class_id INT,
    title VARCHAR(100) NOT NULL,
    start_time DATETIME,
    end_time DATETIME,
    FOREIGN KEY (class_id) REFERENCES Class(id)
);

CREATE TABLE Meeting_Participants (
    meeting_id INT,
    user_id INT,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (meeting_id, user_id),
    FOREIGN KEY (meeting_id) REFERENCES Meeting(id),
    FOREIGN KEY (user_id) REFERENCES User(id)
);

CREATE TABLE Chat_message (
    id INT PRIMARY KEY AUTO_INCREMENT,
    meeting_id INT,
    user_id INT,
    message TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (meeting_id) REFERENCES Meeting(id),
    FOREIGN KEY (user_id) REFERENCES User(id)
);