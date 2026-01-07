"""
Apply schema update for course_grades table
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('LOCAL_DB_HOST', 'localhost'),
    'port': int(os.getenv('LOCAL_DB_PORT', 5432)),
    'database': os.getenv('LOCAL_DB_NAME', 'Lovable'),
    'user': os.getenv('LOCAL_DB_USER', 'postgres'),
    'password': os.getenv('LOCAL_DB_PASSWORD'),
}

# SQL to create course_grades table
CREATE_TABLE_SQL = """
SET search_path TO transform, public;

-- Drop if exists
DROP TABLE IF EXISTS course_grades CASCADE;

-- Create course_grades table
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

-- Create indexes
CREATE INDEX idx_course_grades_user_id ON course_grades(user_id);
CREATE INDEX idx_course_grades_course_id ON course_grades(course_id);
CREATE INDEX idx_course_grades_assessment_type ON course_grades(assessment_type);

-- Add comment
COMMENT ON TABLE course_grades IS 'Offline/summative assessment grades (assignments, midterm, final exams)';
"""

def main():
    print("🔧 Cập nhật schema database...")
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        cursor.execute(CREATE_TABLE_SQL)
        conn.commit()
        print("✓ Đã tạo bảng course_grades thành công!")
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM course_grades")
        count = cursor.fetchone()[0]
        print(f"✓ Bảng course_grades đã sẵn sàng (hiện có {count} bản ghi)")
        
    except Exception as e:
        print(f"✗ Lỗi: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    main()
