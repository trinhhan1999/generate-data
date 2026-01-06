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

## Git Workflow

### Push lên GitHub lần đầu

1. **Khởi tạo Git repository (nếu chưa có):**
```bash
git init
```

2. **Thêm files vào staging:**
```bash
git add .
```

3. **Tạo commit đầu tiên:**
```bash
git commit -m "Initial commit: Learning Path Data Generator"
```

4. **Tạo repository trên GitHub:**
   - Truy cập https://github.com/new
   - Đặt tên repo (ví dụ: `learning-path-data-generator`)
   - Chọn Public hoặc Private
   - **KHÔNG** chọn "Initialize with README"
   - Click "Create repository"

5. **Link local repo với GitHub và push:**
```bash
# Thay YOUR_USERNAME và YOUR_REPO_NAME bằng thông tin của bạn
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### Làm việc với Branch (Recommended)

**1. Tạo branch mới cho feature/fix:**
```bash
# Tạo và chuyển sang branch mới
git checkout -b feature/ten-feature

# Hoặc có thể đặt tên theo convention
git checkout -b feature/add-new-persona
git checkout -b fix/quiz-logic
git checkout -b update/readme
```

**2. Làm việc trên branch:**
```bash
# Xem branch hiện tại
git branch

# Chỉnh sửa code...
# Sau đó commit như bình thường
git add .
git commit -m "feat: thêm persona mới"
```

**3. Push branch lên GitHub:**
```bash
# Push lần đầu
git push -u origin feature/ten-feature

# Các lần sau
git push
```

**4. Tạo Pull Request trên GitHub:**
   - Truy cập repository trên GitHub
   - Click "Compare & pull request"
   - Viết mô tả thay đổi
   - Click "Create pull request"
   - Review và merge

**5. Merge branch vào main (local):**
```bash
# Chuyển về main
git checkout main

# Pull code mới nhất từ remote
git pull origin main

# Merge branch vào main
git merge feature/ten-feature

# Push main lên remote
git push
```

**6. Xóa branch sau khi merge:**
```bash
# Xóa branch local
git branch -d feature/ten-feature

# Xóa branch trên GitHub
git push origin --delete feature/ten-feature
```

**7. Các lệnh branch hữu ích:**
```bash
git branch              # Xem danh sách branches local
git branch -a           # Xem tất cả branches (cả remote)
git branch -r           # Xem branches trên remote
git checkout main       # Chuyển về main
git branch -D branch-name  # Xóa branch force (nếu chưa merge)
```

### Cập nhật code trực tiếp trên main

```bash
# Xem thay đổi
git status

# Thêm files đã sửa
git add .

# Commit với message
git commit -m "Update: mô tả thay đổi"

# Push lên GitHub
git push
```

### Cấu hình Git user (lần đầu)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Kiểm tra remote

```bash
git remote -v
```

### Xóa và thêm lại remote (nếu cần)

```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

## Lưu ý

- File `.env` chứa thông tin nhạy cảm, không push lên Git (đã được bảo vệ bởi `.gitignore`)
- File `.env.example` là template, cần copy thành `.env` và điền thông tin
- Script tự động xóa dữ liệu cũ trước khi sinh dữ liệu mới
- Thời gian sinh: 2025-11-01 đến 2026-01-01 (2 tháng)

## License

MIT
