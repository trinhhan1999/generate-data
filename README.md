# Learning Path Data Generator

Script Python để sinh dữ liệu giả lập hành vi học tập trên LMS (Learning Management System) cho hệ thống recommendation.

## Mô tả

Project này sinh dữ liệu thực tế cho 20 sinh viên trong 2 tháng, bao gồm:
- Hành vi học bài (lessons)
- Làm quiz và retry với learning curve
- Tương tác với nội dung (video, text, pdf)
- Phân loại persona (Giỏi, Trung bình, Yếu, Bỏ cuộc)

## Cấu trúc Database

18 bảng dữ liệu:
- **User data**: profiles, user_roles, enrollments
- **Content**: courses, modules, lessons, quizzes, questions
- **Activities**: activity_logs, user_sessions, lesson_progress
- **Quiz data**: quiz_attempts, question_responses, quiz_interaction_logs
- **Interactions**: interaction_logs, reading_behavior_logs, forum_posts, forum_reactions

## Yêu cầu

- Python 3.11+
- PostgreSQL
- DBeaver (khuyến nghị)

## Cài đặt

1. Clone repository:
```bash
git clone <your-repo-url>
cd "generate data learning path"
```

2. Tạo virtual environment:
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
```

3. Cài đặt dependencies:
```bash
pip install psycopg2-binary python-dotenv
```

4. Tạo file `.env` với thông tin database:
```env
LOCAL_DB_HOST=localhost
LOCAL_DB_PORT=5432
LOCAL_DB_NAME=Lovable
LOCAL_DB_USER=postgres
LOCAL_DB_PASSWORD=your_password
LOCAL_DB_SCHEMA=transform
```

## Sử dụng

1. Tạo schema trong PostgreSQL:
```bash
# Chạy file create_schema.sql trong DBeaver hoặc psql
```

2. Import dữ liệu nội dung khóa học (nếu cần):
```bash
python import_to_postgres.py
```

3. Sinh dữ liệu hành vi học tập:
```bash
python generate_learning_data.py
```

## Tính năng

### Phân loại Persona
- **Diligent (20%)**: Học chăm, hoàn thành 85-100%, retry quiz để đạt điểm cao
- **Average (40%)**: Học đều, hoàn thành 60-90%
- **Struggling (25%)**: Gặp khó khăn, hoàn thành 35-65%
- **Dropout (15%)**: Bỏ cuộc sau 2-3 tuần

### Dữ liệu sinh ra
- **Activity logs**: View/Complete cho lessons, quizzes với timestamps hợp lý
- **Quiz attempts**: Lên đến 3 lần, điểm tăng dần qua các lần (learning curve)
- **Interactions**: View, hint_request, answer changes, submit với metadata chi tiết
- **Reading behavior**: Scroll, time spent, completion rate

### Logic thời gian
- ✅ Enrollment luôn trước activities
- ✅ View trước Complete
- ✅ Quiz start trước submit
- ✅ Timestamps tuân theo causality

## Kết quả mẫu

```
📊 THỐNG KÊ DỮ LIỆU
  profiles                      :     20 bản ghi
  enrollments                   :     84 bản ghi
  user_sessions                 :    830 bản ghi
  activity_logs                 :   4742 bản ghi
  lesson_progress               :   1164 bản ghi
  quiz_attempts                 :    849 bản ghi
  question_responses            :   3051 bản ghi
  quiz_interaction_logs         :  10415 bản ghi
  interaction_logs              :   3279 bản ghi
```

## Cấu trúc thư mục

```
.
├── .env                          # Cấu hình database (không commit)
├── .gitignore                    # Git ignore rules
├── create_schema.sql             # Schema definition
├── database-export-2026-01-02.json  # Dữ liệu courses/modules/lessons
├── generate_learning_data.py     # Script chính sinh dữ liệu
├── import_to_postgres.py         # Import dữ liệu ban đầu
└── README.md                     # File này
```

## Lưu ý

- File `.env` chứa thông tin nhạy cảm, không push lên Git
- Script tự động xóa dữ liệu cũ trước khi sinh dữ liệu mới
- Thời gian sinh: 2025-11-01 đến 2026-01-01 (2 tháng)

## License

MIT
