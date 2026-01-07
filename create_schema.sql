-- Learning Path Recommendation System Database Schema
-- Created: 2026-01-05

-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS transform;

-- Set search path to use transform schema
SET search_path TO transform, public;

-- Drop tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS course_grades CASCADE;
DROP TABLE IF EXISTS reading_behavior_logs CASCADE;
DROP TABLE IF EXISTS quiz_interaction_logs CASCADE;
DROP TABLE IF EXISTS question_responses CASCADE;
DROP TABLE IF EXISTS quiz_attempts CASCADE;
DROP TABLE IF EXISTS questions CASCADE;
DROP TABLE IF EXISTS quizzes CASCADE;
DROP TABLE IF EXISTS lesson_progress CASCADE;
DROP TABLE IF EXISTS interaction_logs CASCADE;
DROP TABLE IF EXISTS activity_logs CASCADE;
DROP TABLE IF EXISTS user_sessions CASCADE;
DROP TABLE IF EXISTS forum_reactions CASCADE;
DROP TABLE IF EXISTS forum_posts CASCADE;
DROP TABLE IF EXISTS enrollments CASCADE;
DROP TABLE IF EXISTS lessons CASCADE;
DROP TABLE IF EXISTS modules CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS user_roles CASCADE;
DROP TABLE IF EXISTS profiles CASCADE;

-- Create tables

-- Profiles table
CREATE TABLE profiles (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    full_name VARCHAR(255),
    avatar_url TEXT,
    bio TEXT,
    preferred_learning_style VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- User roles table
CREATE TABLE user_roles (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Courses table
CREATE TABLE courses (
    id UUID PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    thumbnail_url TEXT,
    instructor_id UUID,
    is_published BOOLEAN DEFAULT false,
    difficulty_level VARCHAR(50),
    estimated_hours INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Modules table
CREATE TABLE modules (
    id UUID PRIMARY KEY,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    order_index INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Lessons table
CREATE TABLE lessons (
    id UUID PRIMARY KEY,
    module_id UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    content_type VARCHAR(50),
    content_url TEXT,
    content_text TEXT,
    order_index INTEGER NOT NULL,
    estimated_minutes INTEGER,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enrollments table
CREATE TABLE enrollments (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    status VARCHAR(50),
    progress_percentage INTEGER DEFAULT 0,
    enrolled_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Forum posts table
CREATE TABLE forum_posts (
    id UUID PRIMARY KEY,
    lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    parent_post_id UUID REFERENCES forum_posts(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_pinned BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Forum reactions table
CREATE TABLE forum_reactions (
    id UUID PRIMARY KEY,
    post_id UUID NOT NULL REFERENCES forum_posts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    reaction_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- User sessions table
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    session_token VARCHAR(500),
    device_info JSONB,
    ip_address VARCHAR(50),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true
);

-- Activity logs table
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    session_id UUID REFERENCES user_sessions(id) ON DELETE SET NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    action_type VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    duration_ms INTEGER,
    metadata JSONB,
    client_info JSONB
);

-- Interaction logs table
CREATE TABLE interaction_logs (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE,
    session_id UUID REFERENCES user_sessions(id) ON DELETE SET NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    element_id VARCHAR(255),
    interaction_type VARCHAR(100) NOT NULL,
    is_correct BOOLEAN,
    attempt_number INTEGER,
    time_spent_ms INTEGER,
    metadata JSONB
);

-- Lesson progress table
CREATE TABLE lesson_progress (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    lesson_id UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    is_completed BOOLEAN DEFAULT false,
    progress_percentage INTEGER DEFAULT 0,
    time_spent_seconds INTEGER DEFAULT 0,
    last_position JSONB,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

-- Quizzes table
CREATE TABLE quizzes (
    id UUID PRIMARY KEY,
    module_id UUID REFERENCES modules(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    time_limit_minutes INTEGER,
    max_attempts INTEGER,
    passing_score INTEGER,
    shuffle_questions BOOLEAN DEFAULT false,
    show_correct_answers BOOLEAN DEFAULT true,
    order_index INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Questions table
CREATE TABLE questions (
    id UUID PRIMARY KEY,
    quiz_id UUID NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    options JSONB,
    correct_answer TEXT,
    explanation TEXT,
    points INTEGER DEFAULT 1,
    order_index INTEGER NOT NULL,
    topic_tags JSONB,
    difficulty_level VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Quiz attempts table
CREATE TABLE quiz_attempts (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    quiz_id UUID NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    attempt_number INTEGER,
    score INTEGER,
    max_score INTEGER,
    is_passed BOOLEAN,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    time_spent_seconds INTEGER
);

-- Question responses table
CREATE TABLE question_responses (
    id UUID PRIMARY KEY,
    attempt_id UUID NOT NULL REFERENCES quiz_attempts(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    user_answer TEXT,
    is_correct BOOLEAN,
    points_earned INTEGER DEFAULT 0,
    time_spent_seconds INTEGER,
    answered_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Quiz interaction logs table
CREATE TABLE quiz_interaction_logs (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    quiz_id UUID REFERENCES quizzes(id) ON DELETE CASCADE,
    attempt_id UUID REFERENCES quiz_attempts(id) ON DELETE CASCADE,
    question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    action_type VARCHAR(100) NOT NULL,
    answer_given TEXT,
    is_correct BOOLEAN,
    time_spent_ms INTEGER,
    answer_changes_count INTEGER,
    hint_used BOOLEAN,
    metadata JSONB
);

-- Reading behavior logs table
CREATE TABLE reading_behavior_logs (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE,
    session_id UUID REFERENCES user_sessions(id) ON DELETE SET NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    page_number INTEGER,
    dwell_time_ms INTEGER,
    scroll_depth_percent INTEGER,
    action_type VARCHAR(100),
    position_data JSONB,
    metadata JSONB
);

-- Course grades table (Offline/Summative Assessments)
CREATE TABLE course_grades (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    assessment_type VARCHAR(50) NOT NULL CHECK (assessment_type IN ('assignment', 'midterm', 'final')),
    title VARCHAR(255) NOT NULL,
    score NUMERIC(4, 2) NOT NULL CHECK (score >= 0 AND score <= 10),
    weight NUMERIC(3, 2) NOT NULL CHECK (weight >= 0 AND weight <= 1),
    graded_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX idx_profiles_user_id ON profiles(user_id);
CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_modules_course_id ON modules(course_id);
CREATE INDEX idx_lessons_module_id ON lessons(module_id);
CREATE INDEX idx_enrollments_user_id ON enrollments(user_id);
CREATE INDEX idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX idx_forum_posts_lesson_id ON forum_posts(lesson_id);
CREATE INDEX idx_forum_posts_user_id ON forum_posts(user_id);
CREATE INDEX idx_forum_reactions_post_id ON forum_reactions(post_id);
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_session_id ON activity_logs(session_id);
CREATE INDEX idx_activity_logs_timestamp ON activity_logs(timestamp);
CREATE INDEX idx_interaction_logs_user_id ON interaction_logs(user_id);
CREATE INDEX idx_interaction_logs_lesson_id ON interaction_logs(lesson_id);
CREATE INDEX idx_lesson_progress_user_id ON lesson_progress(user_id);
CREATE INDEX idx_lesson_progress_lesson_id ON lesson_progress(lesson_id);
CREATE INDEX idx_quizzes_module_id ON quizzes(module_id);
CREATE INDEX idx_questions_quiz_id ON questions(quiz_id);
CREATE INDEX idx_quiz_attempts_user_id ON quiz_attempts(user_id);
CREATE INDEX idx_quiz_attempts_quiz_id ON quiz_attempts(quiz_id);
CREATE INDEX idx_question_responses_attempt_id ON question_responses(attempt_id);
CREATE INDEX idx_question_responses_question_id ON question_responses(question_id);
CREATE INDEX idx_quiz_interaction_logs_user_id ON quiz_interaction_logs(user_id);
CREATE INDEX idx_reading_behavior_logs_user_id ON reading_behavior_logs(user_id);
CREATE INDEX idx_reading_behavior_logs_lesson_id ON reading_behavior_logs(lesson_id);
CREATE INDEX idx_course_grades_user_id ON course_grades(user_id);
CREATE INDEX idx_course_grades_course_id ON course_grades(course_id);
CREATE INDEX idx_course_grades_assessment_type ON course_grades(assessment_type);

-- Comments
COMMENT ON TABLE profiles IS 'User profile information';
COMMENT ON TABLE courses IS 'Learning courses';
COMMENT ON TABLE modules IS 'Course modules';
COMMENT ON TABLE lessons IS 'Individual lessons within modules';
COMMENT ON TABLE enrollments IS 'User course enrollments';
COMMENT ON TABLE activity_logs IS 'User activity tracking';
COMMENT ON TABLE lesson_progress IS 'User progress on lessons';
COMMENT ON TABLE quizzes IS 'Quizzes associated with lessons';
COMMENT ON TABLE questions IS 'Quiz questions';
COMMENT ON TABLE quiz_attempts IS 'User quiz attempts';
COMMENT ON TABLE question_responses IS 'User answers to quiz questions';
COMMENT ON TABLE user_sessions IS 'User session tracking';
COMMENT ON TABLE course_grades IS 'Offline/summative assessment grades (assignments, midterm, final exams)';
COMMENT ON TABLE interaction_logs IS 'User interaction events';
COMMENT ON TABLE quiz_interaction_logs IS 'Quiz-specific interaction events';
COMMENT ON TABLE reading_behavior_logs IS 'Reading behavior analytics';
