"""
Validate course_grades data
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
    print("🔍 Kiểm tra dữ liệu course_grades...\n")
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SET search_path TO transform, public")
    
    # 1. Distribution by assessment type
    print("1️⃣ Phân bố theo loại đánh giá:")
    cursor.execute("""
        SELECT assessment_type, COUNT(*), 
               ROUND(AVG(score), 2) as avg_score,
               ROUND(MIN(score), 2) as min_score,
               ROUND(MAX(score), 2) as max_score
        FROM course_grades
        GROUP BY assessment_type
        ORDER BY assessment_type
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]:15s}: {row[1]:3d} bản ghi | Avg: {row[2]:.2f} | Min: {row[3]:.2f} | Max: {row[4]:.2f}")
    
    # 2. Sample data with user info
    print("\n2️⃣ Mẫu dữ liệu (5 users ngẫu nhiên):")
    cursor.execute("""
        SELECT p.full_name, c.title, cg.assessment_type, cg.title, cg.score, cg.graded_at
        FROM course_grades cg
        JOIN profiles p ON cg.user_id = p.user_id
        JOIN courses c ON cg.course_id = c.id
        ORDER BY p.full_name, cg.graded_at
        LIMIT 15
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]:20s} | {row[1][:25]:25s} | {row[2]:10s} | {row[3]:20s} | {row[4]:.1f}/10 | {row[5].strftime('%Y-%m-%d')}")
    
    # 3. Check timeline consistency (graded_at > enrolled_at)
    print("\n3️⃣ Kiểm tra timeline consistency:")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM course_grades cg
        JOIN enrollments e ON cg.user_id = e.user_id AND cg.course_id = e.course_id
        WHERE cg.graded_at < e.enrolled_at
    """)
    errors = cursor.fetchone()[0]
    print(f"   ❌ Lỗi timeline (graded_at < enrolled_at): {errors}")
    
    # 4. Check score correlation with quiz performance by persona
    print("\n4️⃣ Tương quan điểm course_grades vs quiz (theo persona):")
    cursor.execute("""
        WITH quiz_avg AS (
            SELECT qa.user_id, 
                   AVG(qa.score::float / qa.max_score * 10) as avg_quiz_score
            FROM quiz_attempts qa
            GROUP BY qa.user_id
        ),
        grade_avg AS (
            SELECT cg.user_id,
                   AVG(cg.score) as avg_grade_score
            FROM course_grades cg
            GROUP BY cg.user_id
        )
        SELECT 
            CASE 
                WHEN p.full_name LIKE 'Nguyễn Văn An%' OR p.full_name LIKE 'Trần Thị Bình%' 
                     OR p.full_name LIKE 'Lê Hoàng Cường%' OR p.full_name LIKE 'Phạm Thị Dung%' THEN 'diligent'
                WHEN p.full_name LIKE 'Đỗ Văn Hùng%' OR p.full_name LIKE 'Lý Thị Lan%' 
                     OR p.full_name LIKE 'Phan Văn Khoa%' THEN 'dropout'
                WHEN p.full_name LIKE 'Hoàng Văn Em%' OR p.full_name LIKE 'Vũ Thị Phương%'
                     OR p.full_name LIKE 'Đặng Văn Giang%' OR p.full_name LIKE 'Bùi Thị Hà%'
                     OR p.full_name LIKE 'Ngô Thị Mai%' THEN 'struggling'
                ELSE 'average'
            END as persona,
            COUNT(*) as num_users,
            ROUND(AVG(qa.avg_quiz_score)::numeric, 2) as avg_quiz,
            ROUND(AVG(ga.avg_grade_score)::numeric, 2) as avg_grade
        FROM profiles p
        LEFT JOIN quiz_avg qa ON p.user_id = qa.user_id
        LEFT JOIN grade_avg ga ON p.user_id = ga.user_id
        GROUP BY persona
        ORDER BY avg_grade DESC
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]:12s}: {row[1]:2d} users | Quiz avg: {row[2]:.2f} | Grade avg: {row[3]:.2f}")
    
    # 5. Count outliers (students with very different scores)
    print("\n5️⃣ Phát hiện outliers (điểm bất thường):")
    cursor.execute("""
        WITH user_stats AS (
            SELECT user_id,
                   AVG(score) as avg_score,
                   STDDEV(score) as std_score,
                   MIN(score) as min_score,
                   MAX(score) as max_score
            FROM course_grades
            GROUP BY user_id
            HAVING COUNT(*) >= 3
        )
        SELECT p.full_name, 
               ROUND(us.avg_score, 2) as avg,
               ROUND(us.std_score, 2) as std_dev,
               us.min_score, us.max_score
        FROM user_stats us
        JOIN profiles p ON us.user_id = p.user_id
        WHERE us.std_score > 2.5 OR (us.max_score - us.min_score) > 5
        ORDER BY us.std_score DESC
        LIMIT 10
    """)
    print("   Top 10 users có điểm dao động lớn (potential outliers):")
    for row in cursor.fetchall():
        print(f"   {row[0]:20s} | Avg: {row[1]:.2f} | StdDev: {row[2]:.2f} | Range: {row[3]:.1f}-{row[4]:.1f}")
    
    # 6. Check weight distribution
    print("\n6️⃣ Phân bố trọng số (weight):")
    cursor.execute("""
        SELECT assessment_type, ROUND(AVG(weight), 2) as avg_weight
        FROM course_grades
        GROUP BY assessment_type
        ORDER BY assessment_type
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]:15s}: {row[1]:.0%}")
    
    cursor.close()
    conn.close()
    print("\n✓ Hoàn thành kiểm tra!")

if __name__ == '__main__':
    main()
