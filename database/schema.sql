-- Database Schema for AI-Powered Automated Recruitment System
CREATE DATABASE IF NOT EXISTS recruitment_db;
USE recruitment_db;

-- 1. Jobs Table
CREATE TABLE IF NOT EXISTS jobs (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    required_skills JSON NOT NULL,
    minimum_experience VARCHAR(100) DEFAULT '0-2 years',
    minimum_resume_score INT DEFAULT 70,
    test_passing_score INT DEFAULT 80,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Candidates Table
CREATE TABLE IF NOT EXISTS candidates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    job_id VARCHAR(64) NOT NULL,
    resume_filename VARCHAR(255) DEFAULT NULL,
    resume_text LONGTEXT DEFAULT NULL,
    resume_score INT DEFAULT 0,
    resume_analysis JSON DEFAULT NULL,
    test_token VARCHAR(128) UNIQUE DEFAULT NULL,
    test_token_expires_at DATETIME DEFAULT NULL,
    test_status ENUM('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'EXPIRED') DEFAULT 'NOT_STARTED',
    test_score INT DEFAULT 0,
    application_status ENUM(
        'RECEIVED', 
        'RESUME_PROCESSING', 
        'RESUME_REJECTED', 
        'RESUME_SHORTLISTED', 
        'TEST_SENT', 
        'TEST_STARTED', 
        'TEST_COMPLETED', 
        'TEST_FAILED', 
        'SELECTED', 
        'OFFER_SENT', 
        'ERROR'
    ) DEFAULT 'RECEIVED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_candidate_job (email, job_id),
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Test Results Table
CREATE TABLE IF NOT EXISTS test_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    total_questions INT NOT NULL,
    correct_answers INT NOT NULL,
    score INT NOT NULL,
    test_answers JSON DEFAULT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Workflow Logs Table
CREATE TABLE IF NOT EXISTS workflow_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT DEFAULT NULL,
    candidate_email VARCHAR(255) NOT NULL,
    workflow_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    message TEXT DEFAULT NULL,
    resume_score INT DEFAULT NULL,
    test_score INT DEFAULT NULL,
    application_status VARCHAR(50) DEFAULT NULL,
    error_message TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed Default Job
INSERT INTO jobs (id, title, description, required_skills, minimum_experience, minimum_resume_score, test_passing_score)
VALUES (
    'python-ml-developer-001',
    'Python / Machine Learning Developer',
    'We are looking for a Python/Machine Learning developer who can build APIs, work with ML models and databases, and develop automation systems.',
    '["Python", "FastAPI", "SQL", "Machine Learning", "Pandas", "NumPy", "REST API", "Git"]',
    '0-2 years',
    70,
    80
) ON DUPLICATE KEY UPDATE title=VALUES(title);
