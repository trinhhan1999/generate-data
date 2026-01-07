"""
Advanced validation - check correlation and outliers
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

def main():
    print("🔍 Chi tiết validation course_grades...\n")
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SET search_path TO transform, public")
    
    # Get sample students with their quiz and grade performance
    print("📊 So sánh Quiz Performance vs Course Grades (Top 20 users):\n")
    cursor.execute("""
        WITH quiz_stats AS (
            SELECT qa.user_id,
                   COUNT(*) as quiz_count,
                   AVG(qa.score::float / qa.max_score * 10) as avg_quiz_score,
                   MAX(qa.score::float / qa.max_score * 10) as max_quiz_score
            FROM quiz_attempts qa
            GROUP BY qa.user_id
        ),
        grade_stats AS (
            SELECT cg.user_id,
                   COUNT(*) as grade_count,
                   AVG(cg.score) as avg_grade,
                   STDDEV(cg.score) as stddev_grade,
                   MIN(cg.score) as min_grade,
                   MAX(cg.score) as max_grade
            FROM course_grades cg
            GROUP BY cg.user_id
        )
        SELECT 
            p.full_name,
            ROUND(qs.avg_quiz_score::numeric, 2) as quiz_avg,
            ROUND(gs.avg_grade::numeric, 2) as grade_avg,
            ROUND(gs.stddev_grade::numeric, 2) as grade_std,
            gs.min_grade,
            gs.max_grade,
            gs.grade_count
        FROM profiles p
        JOIN quiz_stats qs ON p.user_id = qs.user_id
        JOIN grade_stats gs ON p.user_id = gs.user_id
        ORDER BY gs.avg_grade DESC
        LIMIT 20
    """)
    
    print(f"{'Tên':20s} | {'Quiz Avg':9s} | {'Grade Avg':10s} | {'Std Dev':8s} | {'Min':5s} | {'Max':5s} | Grades")
    print("-" * 90)
    for row in cursor.fetchall():
        print(f"{row[0]:20s} | {row[1]:9.2f} | {row[2]:10.2f} | {row[3]:8.2f} | {row[4]:5.1f} | {row[5]:5.1f} | {row[6]:3d}")
    
    # Check specific examples of outliers
    print("\n\n🎯 Ví dụ outliers (students với điểm bất thường):\n")
    cursor.execute("""
        WITH user_perf AS (
            SELECT 
                cg.user_id,
                p.full_name,
                AVG(qa.score::float / qa.max_score * 10) as avg_quiz,
                AVG(cg.score) as avg_grade
            FROM course_grades cg
            JOIN profiles p ON cg.user_id = p.user_id
            LEFT JOIN quiz_attempts qa ON cg.user_id = qa.user_id
            GROUP BY cg.user_id, p.full_name
        )
        SELECT full_name,
               ROUND(avg_quiz::numeric, 2) as quiz_avg,
               ROUND(avg_grade::numeric, 2) as grade_avg,
               ROUND((avg_grade - avg_quiz)::numeric, 2) as difference
        FROM user_perf
        WHERE ABS(avg_grade - avg_quiz) > 2.0
        ORDER BY ABS(avg_grade - avg_quiz) DESC
        LIMIT 10
    """)
    
    print(f"{'Tên':20s} | {'Quiz Avg':9s} | {'Grade Avg':10s} | {'Diff':10s} | {'Type'}")
    print("-" * 80)
    for row in cursor.fetchall():
        outlier_type = "↑ BETTER" if row[3] > 0 else "↓ WORSE"
        print(f"{row[0]:20s} | {row[1]:9.2f} | {row[2]:10.2f} | {row[3]:+10.2f} | {outlier_type}")
    
    # Timeline verification
    print("\n\n📅 Kiểm tra timeline chi tiết (sample 10 users):\n")
    cursor.execute("""
        SELECT p.full_name, c.title, e.enrolled_at, cg.assessment_type, cg.graded_at,
               EXTRACT(day FROM (cg.graded_at - e.enrolled_at)) as days_after_enroll
        FROM course_grades cg
        JOIN profiles p ON cg.user_id = p.user_id
        JOIN courses c ON cg.course_id = c.id
        JOIN enrollments e ON cg.user_id = e.user_id AND cg.course_id = e.course_id
        ORDER BY p.full_name, e.enrolled_at, cg.graded_at
        LIMIT 30
    """)
    
    print(f"{'User':20s} | {'Course':25s} | {'Type':10s} | {'Days After'}")
    print("-" * 80)
    for row in cursor.fetchall():
        print(f"{row[0]:20s} | {row[1][:25]:25s} | {row[3]:10s} | {int(row[5]):3d} days")
    
    cursor.close()
    conn.close()
    print("\n✓ Hoàn thành!")

if __name__ == '__main__':
    main()
