-- Create database
CREATE DATABASE IF NOT EXISTS browser_extension;
USE browser_extension;

-- Users table (for session management)
CREATE TABLE users (
    user_id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Chat history table
CREATE TABLE chat_sessions (
    chat_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    message_id VARCHAR(255),
    message_type ENUM('user', 'assistant'),
    message_text TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Browser activity tracking
CREATE TABLE browser_activities (
    activity_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    url TEXT NOT NULL,
    domain VARCHAR(255),
    page_title TEXT,
    activity_type ENUM('page_visit', 'click', 'scroll', 'form_input', 'tab_change', 'search'),
    element_details JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_seconds INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Daily session summary
CREATE TABLE daily_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    total_pages_visited INT DEFAULT 0,
    total_interactions INT DEFAULT 0,
    chat_messages_count INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Create indexes for performance
CREATE INDEX idx_user_sessions ON chat_sessions(user_id, session_id);
CREATE INDEX idx_activities_time ON browser_activities(timestamp);
CREATE INDEX idx_activities_user ON browser_activities(user_id, session_id);