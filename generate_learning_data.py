"""
Data Simulation Script for Learning Path Recommendation System
Generate realistic student learning behavior data for 2 months, 20 students
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import Json
import os
from dotenv import load_dotenv

load_dotenv()

# Constants
START_DATE = datetime(2025, 11, 1, tzinfo=None)
END_DATE = datetime(2026, 1, 1, tzinfo=None)
TOTAL_DAYS = (END_DATE - START_DATE).days

# Student personas
PERSONA_DILIGENT = "diligent"      # 20% - Giỏi
PERSONA_AVERAGE = "average"        # 40% - Khá/TB
PERSONA_STRUGGLING = "struggling"  # 25% - Yếu
PERSONA_DROPOUT = "dropout"        # 15% - Bỏ cuộc

VIETNAMESE_NAMES = [
    "Nguyễn Văn An", "Trần Thị Bình", "Lê Hoàng Cường", "Phạm Thị Dung",
    "Hoàng Văn Em", "Vũ Thị Phương", "Đặng Văn Giang", "Bùi Thị Hà",
    "Đỗ Văn Hùng", "Lý Thị Lan", "Phan Văn Khoa", "Ngô Thị Mai",
    "Trương Văn Nam", "Đinh Thị Oanh", "Mai Văn Phúc", "Dương Thị Quỳnh",
    "Võ Văn Sơn", "Tô Thị Tâm", "Hồ Văn Tùng", "Cao Thị Uyên"
]

# Element definitions for interaction logs
ELEMENT_DEFINITIONS = {
    'video': {
        'video_player_play': {
            'name': 'Play Button',
            'type': 'button',
            'context': 'video_control',
            'interactions': ['click'],
            'metadata_extras': lambda: {'position': random.choice(['start', 'middle', 'end'])}
        },
        'video_player_pause': {
            'name': 'Pause Button',
            'type': 'button',
            'context': 'video_control',
            'interactions': ['click'],
            'metadata_extras': lambda: {'timestamp': f"{random.randint(0, 300)}s"}
        },
        'video_player_seek': {
            'name': 'Video Seekbar',
            'type': 'slider',
            'context': 'video_control',
            'interactions': ['drag', 'click'],
            'metadata_extras': lambda: {'seek_to': f"{random.randint(0, 100)}%"}
        },
        'video_volume': {
            'name': 'Volume Control',
            'type': 'slider',
            'context': 'video_control',
            'interactions': ['drag', 'click'],
            'metadata_extras': lambda: {'volume_level': random.randint(0, 100)}
        },
        'video_fullscreen': {
            'name': 'Fullscreen Button',
            'type': 'button',
            'context': 'video_control',
            'interactions': ['click'],
            'metadata_extras': lambda: {'fullscreen': random.choice([True, False])}
        },
        'video_speed': {
            'name': 'Playback Speed',
            'type': 'dropdown',
            'context': 'video_control',
            'interactions': ['click'],
            'metadata_extras': lambda: {'speed': random.choice(['0.5x', '0.75x', '1x', '1.25x', '1.5x', '2x'])}
        }
    },
    'text': {
        'text_area_scroll': {
            'name': 'Main Content Area',
            'type': 'container',
            'context': 'content_view',
            'interactions': ['scroll'],
            'metadata_extras': lambda: {'scroll_depth': random.randint(10, 100)}
        },
        'heading_click': {
            'name': 'Section Heading',
            'type': 'heading',
            'context': 'navigation',
            'interactions': ['click'],
            'metadata_extras': lambda: {'section': f"section_{random.randint(1, 5)}"}
        },
        'highlight_text': {
            'name': 'Text Selection',
            'type': 'text',
            'context': 'annotation',
            'interactions': ['highlight', 'select'],
            'metadata_extras': lambda: {'text_length': random.randint(10, 100)}
        },
        'code_block': {
            'name': 'Code Example',
            'type': 'code_block',
            'context': 'content_view',
            'interactions': ['click', 'copy'],
            'metadata_extras': lambda: {'language': random.choice(['python', 'javascript', 'sql'])}
        },
        'image_zoom': {
            'name': 'Image Viewer',
            'type': 'image',
            'context': 'media_view',
            'interactions': ['click', 'zoom'],
            'metadata_extras': lambda: {'zoom_level': random.choice([100, 150, 200])}
        },
        'note_button': {
            'name': 'Take Notes Button',
            'type': 'button',
            'context': 'annotation',
            'interactions': ['click'],
            'metadata_extras': lambda: {'note_position': random.randint(0, 100)}
        }
    },
    'pdf': {
        'pdf_scroll': {
            'name': 'PDF Viewer',
            'type': 'container',
            'context': 'document_view',
            'interactions': ['scroll'],
            'metadata_extras': lambda: {'page_number': random.randint(1, 20)}
        },
        'pdf_zoom': {
            'name': 'Zoom Control',
            'type': 'button',
            'context': 'document_control',
            'interactions': ['click'],
            'metadata_extras': lambda: {'zoom_level': random.choice([75, 100, 125, 150, 200])}
        },
        'pdf_download': {
            'name': 'Download PDF Button',
            'type': 'button',
            'context': 'document_control',
            'interactions': ['click'],
            'metadata_extras': lambda: {'file_size': f"{random.randint(100, 5000)}KB"}
        },
        'pdf_print': {
            'name': 'Print Button',
            'type': 'button',
            'context': 'document_control',
            'interactions': ['click'],
            'metadata_extras': lambda: {'pages_to_print': random.randint(1, 10)}
        }
    },
    'navigation': {
        'nav_next': {
            'name': 'Next Lesson Button',
            'type': 'button',
            'context': 'navigation',
            'interactions': ['click'],
            'metadata_extras': lambda: {'direction': 'forward'}
        },
        'nav_prev': {
            'name': 'Previous Lesson Button',
            'type': 'button',
            'context': 'navigation',
            'interactions': ['click'],
            'metadata_extras': lambda: {'direction': 'backward'}
        },
        'nav_menu': {
            'name': 'Course Menu',
            'type': 'menu',
            'context': 'navigation',
            'interactions': ['click', 'hover'],
            'metadata_extras': lambda: {'menu_section': random.choice(['courses', 'lessons', 'quizzes'])}
        },
        'bookmark': {
            'name': 'Bookmark Button',
            'type': 'button',
            'context': 'annotation',
            'interactions': ['click'],
            'metadata_extras': lambda: {'bookmarked': random.choice([True, False])}
        }
    },
    'quiz': {
        'quiz_start_btn': {
            'name': 'Start Quiz Button',
            'type': 'button',
            'context': 'quiz_control',
            'interactions': ['click'],
            'metadata_extras': lambda: {'quiz_type': random.choice(['multiple_choice', 'true_false'])}
        },
        'quiz_submit_btn': {
            'name': 'Submit Answer Button',
            'type': 'button',
            'context': 'quiz_control',
            'interactions': ['click'],
            'metadata_extras': lambda: {'question_number': random.randint(1, 10)}
        },
        'quiz_option': {
            'name': 'Answer Option',
            'type': 'radio_button',
            'context': 'quiz_interaction',
            'interactions': ['click'],
            'metadata_extras': lambda: {'option': random.choice(['A', 'B', 'C', 'D'])}
        }
    }
}


class DataGenerator:
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.conn = None
        self.cursor = None
        
        # Store existing data
        self.courses = []
        self.modules = []
        self.lessons = []
        self.quizzes = []
        self.questions = []
        
        # Generated data
        self.users = []
        self.personas = {}
        
    def connect(self):
        """Connect to database"""
        config = {k: v for k, v in self.db_config.items() if k != 'schema'}
        self.conn = psycopg2.connect(**config)
        self.cursor = self.conn.cursor()
        schema = self.db_config.get('schema', 'public')
        self.cursor.execute(f"SET search_path TO {schema}, public")
        self.conn.commit()
        print(f"✓ Kết nối database thành công! (Schema: {schema})")
    
    def disconnect(self):
        """Disconnect from database"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("✓ Đã đóng kết nối database")
    
    def clear_behavior_data(self):
        """Clear all behavior data, keep course content"""
        print("\n🗑️  Xóa dữ liệu hành vi cũ...")
        
        tables_to_clear = [
            'reading_behavior_logs',
            'quiz_interaction_logs',
            'question_responses',
            'quiz_attempts',
            'interaction_logs',
            'lesson_progress',
            'activity_logs',
            'user_sessions',
            'enrollments',
            'user_roles',
            'profiles'
        ]
        
        for table in tables_to_clear:
            self.cursor.execute(f"DELETE FROM {table}")
            print(f"  ✓ Đã xóa: {table}")
        
        self.conn.commit()
        print("✓ Hoàn thành xóa dữ liệu cũ\n")
    
    def load_existing_content(self):
        """Load existing course content"""
        print("📚 Đọc dữ liệu nội dung khóa học...")
        
        # Load courses
        self.cursor.execute("SELECT id, title, difficulty_level FROM courses ORDER BY created_at")
        self.courses = [{'id': row[0], 'title': row[1], 'difficulty': row[2]} for row in self.cursor.fetchall()]
        
        # Load modules
        self.cursor.execute("SELECT id, course_id, title, order_index FROM modules ORDER BY course_id, order_index")
        self.modules = [{'id': row[0], 'course_id': row[1], 'title': row[2], 'order': row[3]} for row in self.cursor.fetchall()]
        
        # Load lessons
        self.cursor.execute("SELECT id, module_id, title, estimated_minutes, order_index FROM lessons ORDER BY module_id, order_index")
        self.lessons = [{'id': row[0], 'module_id': row[1], 'title': row[2], 'estimated_minutes': row[3], 'order': row[4]} for row in self.cursor.fetchall()]
        
        # Load quizzes
        self.cursor.execute("SELECT id, module_id, title, passing_score, time_limit_minutes FROM quizzes ORDER BY module_id")
        self.quizzes = [{'id': row[0], 'module_id': row[1], 'title': row[2], 'passing_score': row[3], 'time_limit': row[4]} for row in self.cursor.fetchall()]
        
        # Load questions
        self.cursor.execute("SELECT id, quiz_id, question_type, correct_answer, points FROM questions ORDER BY quiz_id, order_index")
        self.questions = [{'id': row[0], 'quiz_id': row[1], 'type': row[2], 'correct_answer': row[3], 'points': row[4]} for row in self.cursor.fetchall()]
        
        print(f"  ✓ {len(self.courses)} courses")
        print(f"  ✓ {len(self.modules)} modules")
        print(f"  ✓ {len(self.lessons)} lessons")
        print(f"  ✓ {len(self.quizzes)} quizzes")
        print(f"  ✓ {len(self.questions)} questions\n")
    
    def generate_users(self, count: int = 20):
        """Generate user profiles with personas"""
        print(f"👥 Tạo {count} sinh viên...")
        
        # Distribute personas
        personas = (
            [PERSONA_DILIGENT] * 4 +      # 20%
            [PERSONA_AVERAGE] * 8 +       # 40%
            [PERSONA_STRUGGLING] * 5 +    # 25%
            [PERSONA_DROPOUT] * 3         # 15%
        )
        random.shuffle(personas)
        
        for i, name in enumerate(VIETNAMESE_NAMES[:count]):
            user_id = str(uuid.uuid4())
            profile_id = str(uuid.uuid4())
            persona = personas[i]
            
            # Insert profile
            self.cursor.execute("""
                INSERT INTO profiles (id, user_id, full_name, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (profile_id, user_id, name, START_DATE, START_DATE))
            
            # Insert user role
            role_id = str(uuid.uuid4())
            self.cursor.execute("""
                INSERT INTO user_roles (id, user_id, role, created_at)
                VALUES (%s, %s, 'student', %s)
            """, (role_id, user_id, START_DATE))
            
            self.users.append({
                'user_id': user_id,
                'profile_id': profile_id,
                'name': name,
                'persona': persona
            })
            self.personas[user_id] = persona
        
        self.conn.commit()
        print(f"  ✓ Giỏi (diligent): {personas.count(PERSONA_DILIGENT)}")
        print(f"  ✓ Khá/TB (average): {personas.count(PERSONA_AVERAGE)}")
        print(f"  ✓ Yếu (struggling): {personas.count(PERSONA_STRUGGLING)}")
        print(f"  ✓ Bỏ cuộc (dropout): {personas.count(PERSONA_DROPOUT)}\n")
    
    def generate_enrollments(self):
        """Generate course enrollments"""
        print("📝 Tạo enrollments...")
        
        # Initialize dictionaries to track enrollments
        self.user_enrollments = {}  # {user_id: [course_id1, course_id2, ...]}
        self.enrollment_details = {}  # {(user_id, course_id): {'enrolled_at': datetime, 'enrollment_id': str}}
        
        # Each student enrolls in 1-2 courses
        for user in self.users:
            user_id = user['user_id']
            self.user_enrollments[user_id] = []
            
            num_courses = 1 if random.random() < 0.7 else 2
            selected_courses = random.sample(self.courses, num_courses)
            
            for course in selected_courses:
                enrollment_id = str(uuid.uuid4())
                # Set enrolled_at at START_DATE or 1 day before to ensure all activities happen after
                enrolled_at = START_DATE
                
                # Calculate progress based on persona
                persona = user['persona']
                if persona == PERSONA_DILIGENT:
                    progress = random.randint(85, 100)
                    status = 'completed' if progress == 100 else 'active'
                    completed_at = END_DATE if progress == 100 else None
                elif persona == PERSONA_AVERAGE:
                    progress = random.randint(60, 90)
                    status = 'active'
                    completed_at = None
                elif persona == PERSONA_STRUGGLING:
                    progress = random.randint(35, 65)
                    status = 'active'
                    completed_at = None
                else:  # dropout
                    progress = random.randint(10, 40)
                    status = 'inactive'
                    completed_at = None
                
                self.cursor.execute("""
                    INSERT INTO enrollments (id, user_id, course_id, status, progress_percentage, enrolled_at, completed_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (enrollment_id, user_id, course['id'], status, progress, enrolled_at, completed_at))
                
                # Track this enrollment with details
                self.user_enrollments[user_id].append(course['id'])
                self.enrollment_details[(user_id, course['id'])] = {
                    'enrolled_at': enrolled_at,
                    'enrollment_id': enrollment_id
                }
        
        self.conn.commit()
        print(f"  ✓ Đã tạo enrollments\n")
    
    def _ensure_enrollment(self, user_id: str, course_id: str, session_start: datetime, persona: str):
        """Ensure user has enrollment for the course, create if not exists"""
        if user_id not in self.user_enrollments:
            self.user_enrollments[user_id] = []
        
        enrollment_key = (user_id, course_id)
        
        if course_id not in self.user_enrollments[user_id]:
            # Create new enrollment with enrolled_at BEFORE session_start
            enrollment_id = str(uuid.uuid4())
            
            # Set enrolled_at to 1-7 days BEFORE the first session
            enrolled_at = session_start - timedelta(days=random.randint(1, 7))
            
            # Ensure enrolled_at is not before START_DATE
            if enrolled_at < START_DATE:
                enrolled_at = START_DATE
            
            # Set initial progress based on persona
            if persona == PERSONA_DILIGENT:
                progress = random.randint(20, 40)
                status = 'active'
            elif persona == PERSONA_AVERAGE:
                progress = random.randint(10, 30)
                status = 'active'
            elif persona == PERSONA_STRUGGLING:
                progress = random.randint(5, 20)
                status = 'active'
            else:  # dropout
                progress = random.randint(0, 15)
                status = 'active'
            
            self.cursor.execute("""
                INSERT INTO enrollments (id, user_id, course_id, status, progress_percentage, enrolled_at, completed_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (enrollment_id, user_id, course_id, status, progress, enrolled_at, None))
            
            # Track this enrollment with details
            self.user_enrollments[user_id].append(course_id)
            self.enrollment_details[enrollment_key] = {
                'enrolled_at': enrolled_at,
                'enrollment_id': enrollment_id
            }
    
    def get_study_frequency(self, persona: str) -> int:
        """Get weekly study frequency based on persona"""
        if persona == PERSONA_DILIGENT:
            return random.randint(4, 6)
        elif persona == PERSONA_AVERAGE:
            return random.randint(3, 5)
        elif persona == PERSONA_STRUGGLING:
            return random.randint(2, 4)
        else:  # dropout
            return random.randint(1, 3)
    
    def generate_learning_behavior(self):
        """Generate all learning behavior data"""
        print("🎓 Tạo dữ liệu hành vi học tập (2 tháng)...")
        
        for user in self.users:
            user_id = user['user_id']
            persona = user['persona']
            
            # Determine active period
            if persona == PERSONA_DROPOUT:
                # Dropout: active first 2-3 weeks, then stop
                active_days = random.randint(14, 21)
            else:
                active_days = TOTAL_DAYS
            
            # Generate study days
            study_days = []
            current_day = 0
            weekly_frequency = self.get_study_frequency(persona)
            
            while current_day < active_days:
                # Generate study days for this week
                week_days = random.sample(range(7), min(weekly_frequency, 7))
                for day in week_days:
                    study_day = current_day + day
                    if study_day < active_days:
                        study_days.append(study_day)
                current_day += 7
            
            study_days.sort()
            
            # Generate sessions and activities for each study day
            self._generate_user_study_data(user, study_days)
        
        self.conn.commit()
        print("  ✓ Hoàn thành tạo dữ liệu hành vi\n")
    
    def _generate_user_study_data(self, user: Dict, study_days: List[int]):
        """Generate study data for a user"""
        user_id = user['user_id']
        persona = user['persona']
        
        lessons_studied = []
        completed_lessons = set()
        
        # Initialize quiz attempts tracker for this user
        if not hasattr(self, 'quiz_attempts_tracker'):
            self.quiz_attempts_tracker = {}
        
        for day_offset in study_days:
            study_date = START_DATE + timedelta(days=day_offset)
            
            # 1-2 sessions per day
            num_sessions = 1 if random.random() < 0.7 else 2
            
            for session_num in range(num_sessions):
                # Generate session
                session_id = str(uuid.uuid4())
                session_start = study_date + timedelta(
                    hours=random.randint(8, 20),
                    minutes=random.randint(0, 59)
                )
                
                # Session duration based on persona
                if persona == PERSONA_DILIGENT:
                    duration_minutes = random.randint(30, 90)
                elif persona == PERSONA_AVERAGE:
                    duration_minutes = random.randint(20, 60)
                else:
                    duration_minutes = random.randint(10, 40)
                
                session_end = session_start + timedelta(minutes=duration_minutes)
                
                # Insert session
                self.cursor.execute("""
                    INSERT INTO user_sessions (id, user_id, session_token, device_info, started_at, ended_at, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    session_id, user_id, str(uuid.uuid4()),
                    Json({"browser": "Chrome", "os": "Windows", "device": "Desktop"}),
                    session_start, session_end, False
                ))
                
                # Generate activities in this session
                self._generate_session_activities(
                    user_id, session_id, session_start, session_end, persona,
                    lessons_studied, completed_lessons
                )
                
                # After main activities, maybe retry previous quizzes
                self._maybe_retry_previous_quizzes(user_id, session_id, session_start, session_end, persona)
    
    def _generate_session_activities(self, user_id: str, session_id: str, 
                                     session_start: datetime, session_end: datetime,
                                     persona: str, lessons_studied: List, completed_lessons: set):
        """Generate activities within a session"""
        current_time = session_start
        
        # Select course: prioritize from enrollments, occasionally explore new courses
        if user_id in self.user_enrollments and self.user_enrollments[user_id]:
            # 90% of time, study enrolled courses
            if random.random() < 0.90:
                enrolled_course_ids = self.user_enrollments[user_id]
                course = next((c for c in self.courses if c['id'] in enrolled_course_ids), None)
                if not course:
                    course = random.choice(self.courses)
            else:
                # 10% explore new course
                course = random.choice(self.courses)
        else:
            # No enrollments yet, pick any course
            course = random.choice(self.courses)
        
        # Ensure enrollment exists for this course
        # This will create enrollment with enrolled_at BEFORE session_start if needed
        self._ensure_enrollment(user_id, course['id'], session_start, persona)
        
        # View course
        self._log_activity(user_id, session_id, current_time, 'view', 'course', course['id'])
        current_time += timedelta(seconds=random.randint(5, 30))
        
        # Select and study 1-3 lessons
        course_modules = [m for m in self.modules if m['course_id'] == course['id']]
        if not course_modules:
            return
        
        num_lessons_in_session = random.randint(1, 3)
        
        for _ in range(num_lessons_in_session):
            if current_time >= session_end:
                break
            
            # Pick a lesson
            module = random.choice(course_modules)
            module_lessons = [l for l in self.lessons if l['module_id'] == module['id']]
            if not module_lessons:
                continue
            
            lesson = random.choice(module_lessons)
            lesson_id = lesson['id']
            
            # View lesson (action_type='view', duration_ms=NULL)
            self._log_activity(user_id, session_id, current_time, 'view', 'lesson', lesson_id, duration_ms=None)
            current_time += timedelta(seconds=random.randint(2, 10))
            
            # Study lesson
            estimated_min = lesson.get('estimated_minutes', 10) or 10
            
            if persona == PERSONA_DILIGENT:
                actual_duration = estimated_min * random.uniform(0.7, 1.3)
            elif persona == PERSONA_AVERAGE:
                actual_duration = estimated_min * random.uniform(0.3, 1.0)
            else:
                actual_duration = estimated_min * random.uniform(0.1, 0.6)
            
            study_duration = int(actual_duration * 60)  # seconds
            study_duration_ms = study_duration * 1000  # milliseconds
            
            # Reading behavior
            self._log_reading_behavior(user_id, lesson_id, session_id, current_time, study_duration, persona)
            
            # Interactions with content type detection
            # Determine lesson content type (video, text, or pdf)
            # For simplicity, we'll assign based on lesson title keywords or random
            lesson_title = lesson.get('title', '').lower()
            if 'video' in lesson_title or random.random() < 0.2:
                content_type = 'video'
            elif 'pdf' in lesson_title or 'document' in lesson_title or random.random() < 0.1:
                content_type = 'pdf'
            else:
                content_type = 'text'
            
            num_interactions = random.randint(2, 8) if persona == PERSONA_DILIGENT else random.randint(0, 4)
            for _ in range(num_interactions):
                interaction_time = current_time + timedelta(seconds=random.randint(0, study_duration))
                self._log_interaction(user_id, lesson_id, session_id, interaction_time, content_type)
            
            current_time += timedelta(seconds=study_duration)
            
            # Lesson progress
            is_completed = self._should_complete_lesson(persona, lesson_id, completed_lessons)
            if is_completed:
                completed_lessons.add(lesson_id)
                # Log complete action with duration_ms
                self._log_activity(user_id, session_id, current_time, 'complete', 'lesson', lesson_id, duration_ms=study_duration_ms)
            
            self._log_lesson_progress(user_id, lesson_id, session_start, current_time, study_duration, is_completed)
            
            lessons_studied.append(lesson_id)
            
            # Maybe take quiz after lesson
            if is_completed and random.random() < 0.5:  # Increase quiz probability
                module_quiz = next((q for q in self.quizzes if q['module_id'] == module['id']), None)
                if module_quiz:
                    # Track quiz attempts for this user/quiz combination
                    quiz_key = (user_id, module_quiz['id'])
                    
                    # First attempt
                    current_time, score, max_score, is_passed = self._generate_quiz_attempt(
                        user_id, session_id, module_quiz, current_time, persona, attempt_number=1
                    )
                    
                    # Store for potential retry in later sessions
                    if not hasattr(self, 'quiz_attempts_tracker'):
                        self.quiz_attempts_tracker = {}
                    
                    self.quiz_attempts_tracker[quiz_key] = {
                        'attempts': 1,
                        'last_score': score,
                        'max_score': max_score,
                        'is_passed': is_passed,
                        'quiz': module_quiz
                    }
    
    def _should_complete_lesson(self, persona: str, lesson_id: str, completed: set) -> bool:
        """Determine if lesson should be completed"""
        if lesson_id in completed:
            return True
        
        if persona == PERSONA_DILIGENT:
            return random.random() < 0.92
        elif persona == PERSONA_AVERAGE:
            return random.random() < 0.70
        elif persona == PERSONA_STRUGGLING:
            return random.random() < 0.45
        else:
            return random.random() < 0.20
    
    def _get_retry_probability(self, persona: str, is_passed: bool) -> float:
        """
        Get probability that user will retry quiz
        Higher for those who failed, varies by persona
        """
        if is_passed:
            # Passed but want perfect score
            if persona == PERSONA_DILIGENT:
                return 0.70  # 70% chance to retry for perfect score
            elif persona == PERSONA_AVERAGE:
                return 0.40  # 40% chance
            elif persona == PERSONA_STRUGGLING:
                return 0.25  # 25% chance
            else:
                return 0.10  # 10% chance
        else:
            # Failed, want to pass
            if persona == PERSONA_DILIGENT:
                return 0.95  # 95% will retry
            elif persona == PERSONA_AVERAGE:
                return 0.85  # 85% will retry
            elif persona == PERSONA_STRUGGLING:
                return 0.70  # 70% will retry
            else:
                return 0.40  # 40% will retry (dropout students)
    
    def _maybe_retry_previous_quizzes(self, user_id: str, session_id: str, 
                                       session_start: datetime, session_end: datetime, 
                                       persona: str):
        """Check if user wants to retry any previous quiz attempts in this session"""
        if not hasattr(self, 'quiz_attempts_tracker'):
            return
        
        current_time = session_start + timedelta(minutes=random.randint(5, 15))
        
        # Find all quizzes this user has attempted
        user_quizzes = [(quiz_key, data) for quiz_key, data in self.quiz_attempts_tracker.items() 
                       if quiz_key[0] == user_id and data['attempts'] < 3]
        
        if not user_quizzes:
            return
        
        # Decide if user wants to retry any quiz
        for quiz_key, quiz_data in user_quizzes:
            if current_time >= session_end:
                break
            
            # Check retry probability
            retry_prob = self._get_retry_probability(persona, quiz_data['is_passed'])
            if random.random() < retry_prob:
                attempt_num = quiz_data['attempts'] + 1
                quiz = quiz_data['quiz']
                
                # Generate retry attempt
                new_time, score, max_score, is_passed = self._generate_quiz_attempt(
                    user_id, session_id, quiz, current_time, persona,
                    attempt_number=attempt_num, 
                    previous_score=quiz_data['last_score'],
                    max_score=quiz_data['max_score']
                )
                
                # Update tracker
                quiz_data['attempts'] = attempt_num
                quiz_data['last_score'] = score
                quiz_data['is_passed'] = is_passed
                
                current_time = new_time + timedelta(minutes=random.randint(2, 5))
    
    def _log_activity(self, user_id: str, session_id: str, timestamp: datetime,
                      action_type: str, resource_type: str, resource_id: str,
                      duration_ms: int = None, metadata: dict = None):
        """Log activity"""
        activity_id = str(uuid.uuid4())
        if metadata is None:
            metadata = {}
        self.cursor.execute("""
            INSERT INTO activity_logs (id, user_id, session_id, timestamp, action_type, resource_type, resource_id, duration_ms, metadata, client_info)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (activity_id, user_id, session_id, timestamp, action_type, resource_type, resource_id, duration_ms, Json(metadata), Json({})))
    
    def _log_reading_behavior(self, user_id: str, lesson_id: str, session_id: str,
                               timestamp: datetime, duration_ms: int, persona: str):
        """Log reading behavior"""
        log_id = str(uuid.uuid4())
        
        if persona == PERSONA_DILIGENT:
            scroll_depth = random.randint(80, 100)
        elif persona == PERSONA_AVERAGE:
            scroll_depth = random.randint(50, 90)
        else:
            scroll_depth = random.randint(20, 60)
        
        self.cursor.execute("""
            INSERT INTO reading_behavior_logs (id, user_id, lesson_id, session_id, timestamp, 
                                                dwell_time_ms, scroll_depth_percent, action_type, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (log_id, user_id, lesson_id, session_id, timestamp, duration_ms * 1000, scroll_depth, 'reading', Json({})))
    
    def _log_interaction(self, user_id: str, lesson_id: str, session_id: str, 
                         timestamp: datetime, lesson_content_type: str = 'text'):
        """Log interaction with meaningful metadata"""
        log_id = str(uuid.uuid4())
        
        # Determine element category based on lesson content type
        if lesson_content_type == 'video':
            element_category = 'video'
        elif lesson_content_type == 'pdf':
            element_category = 'pdf'
        else:
            element_category = random.choice(['text', 'navigation'])
        
        # Select a random element from the category
        elements = ELEMENT_DEFINITIONS.get(element_category, ELEMENT_DEFINITIONS['text'])
        element_key = random.choice(list(elements.keys()))
        element_def = elements[element_key]
        
        # Generate element_id
        element_id = f"element_{element_key}_{random.randint(1, 99):02d}"
        
        # Select interaction type from available interactions
        interaction_type = random.choice(element_def['interactions'])
        
        # Build metadata
        metadata = {
            'name': element_def['name'],
            'type': element_def['type'],
            'context': element_def['context']
        }
        
        # Add extra metadata specific to this element
        if 'metadata_extras' in element_def:
            extra_metadata = element_def['metadata_extras']()
            metadata.update(extra_metadata)
        
        # Add common fields
        metadata['interaction_count'] = random.randint(1, 5)
        metadata['device_type'] = random.choice(['desktop', 'mobile', 'tablet'])
        
        self.cursor.execute("""
            INSERT INTO interaction_logs (id, user_id, lesson_id, session_id, timestamp,
                                          element_id, interaction_type, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (log_id, user_id, lesson_id, session_id, timestamp, 
              element_id, interaction_type, Json(metadata)))
    
    def _log_lesson_progress(self, user_id: str, lesson_id: str, started_at: datetime,
                              completed_at: datetime, time_spent: int, is_completed: bool):
        """Log lesson progress"""
        progress_id = str(uuid.uuid4())
        progress_pct = 100 if is_completed else random.randint(30, 95)
        
        self.cursor.execute("""
            INSERT INTO lesson_progress (id, user_id, lesson_id, is_completed, progress_percentage,
                                          time_spent_seconds, started_at, completed_at, last_position)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (progress_id, user_id, lesson_id, is_completed, progress_pct, time_spent,
              started_at, completed_at if is_completed else None, Json({})))
    
    def _generate_quiz_attempt(self, user_id: str, session_id: str, quiz: Dict,
                                 start_time: datetime, persona: str, attempt_number: int = 1,
                                 previous_score: int = None, max_score: int = None) -> tuple:
        """
        Generate quiz attempt with support for re-attempts
        Returns: (completed_at, score, max_score, is_passed)
        """
        attempt_id = str(uuid.uuid4())
        quiz_id = quiz['id']
        
        # Start quiz (action_type='start')
        self._log_activity(user_id, session_id, start_time, 'start', 'quiz', quiz_id, duration_ms=None)
        start_time += timedelta(seconds=random.randint(3, 15))
        
        # Get questions for this quiz
        quiz_questions = [q for q in self.questions if q['quiz_id'] == quiz_id]
        if not quiz_questions:
            return start_time, 0, 0, False
        
        if max_score is None:
            max_score = sum(q['points'] for q in quiz_questions)
        
        # Determine passing rate based on persona and attempt number
        # Score improves with each attempt
        if attempt_number == 1:
            # First attempt - base rate (lower to encourage retry)
            if persona == PERSONA_DILIGENT:
                pass_rate = random.uniform(0.70, 0.85)  # Sometimes not perfect
            elif persona == PERSONA_AVERAGE:
                pass_rate = random.uniform(0.50, 0.70)  # Often need retry
            elif persona == PERSONA_STRUGGLING:
                pass_rate = random.uniform(0.30, 0.50)  # Usually fail first time
            else:
                pass_rate = random.uniform(0.10, 0.35)
        else:
            # Subsequent attempts - improved rate
            if previous_score is not None:
                # Calculate improvement
                previous_rate = previous_score / max_score
                
                if persona == PERSONA_DILIGENT:
                    improvement = random.uniform(0.05, 0.15)
                elif persona == PERSONA_AVERAGE:
                    improvement = random.uniform(0.10, 0.20)
                else:
                    improvement = random.uniform(0.15, 0.25)
                
                pass_rate = min(0.98, previous_rate + improvement)
            else:
                pass_rate = random.uniform(0.70, 0.90)
        
        score = int(max_score * pass_rate)
        # Pass if score >= 60% of max_score
        is_passed = score >= (max_score * 0.6)
        
        # Time spent on quiz - decreases with attempts
        base_time_per_question = random.randint(30, 120)
        time_multiplier = 1.0 - (attempt_number - 1) * 0.2  # 20% faster each attempt
        time_multiplier = max(0.5, time_multiplier)  # At least 50% of original time
        
        time_per_question = int(base_time_per_question * time_multiplier)
        time_spent = len(quiz_questions) * time_per_question
        time_spent_ms = time_spent * 1000
        
        completed_at = start_time + timedelta(seconds=time_spent)
        
        # Insert quiz attempt FIRST (with initial score) to satisfy foreign key
        self.cursor.execute("""
            INSERT INTO quiz_attempts (id, user_id, quiz_id, attempt_number, score, max_score,
                                        is_passed, started_at, completed_at, time_spent_seconds)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (attempt_id, user_id, quiz_id, attempt_number, score, max_score, is_passed,
              start_time, completed_at, time_spent))
        
        # Generate question responses with learning curve
        # This returns the ACTUAL score based on questions answered correctly
        actual_score = self._generate_question_responses_with_learning(
            user_id, attempt_id, quiz_questions, start_time, 
            time_per_question, score, max_score, attempt_number, persona
        )
        
        # Update quiz attempt with ACTUAL score from question responses
        # Pass if actual_score >= 60% of max_score
        is_passed = actual_score >= (max_score * 0.6)
        self.cursor.execute("""
            UPDATE quiz_attempts 
            SET score = %s, is_passed = %s
            WHERE id = %s
        """, (actual_score, is_passed, attempt_id))
        
        # Log complete action with metadata containing score and passed
        quiz_metadata = {
            'score': actual_score,
            'max_score': max_score,
            'passed': is_passed,
            'attempt_number': attempt_number
        }
        self._log_activity(user_id, session_id, completed_at, 'complete', 'quiz', quiz_id, 
                          duration_ms=time_spent_ms, metadata=quiz_metadata)
        
        return completed_at + timedelta(seconds=random.randint(10, 30)), actual_score, max_score, is_passed
        self._log_activity(user_id, session_id, completed_at, 'complete', 'quiz', quiz_id, 
                          duration_ms=time_spent_ms, metadata=quiz_metadata)
        
        return completed_at + timedelta(seconds=random.randint(10, 30)), actual_score, max_score, is_passed
    
    def _generate_question_responses_with_learning(self, user_id: str, attempt_id: str,
                                                    quiz_questions: List[Dict], start_time: datetime,
                                                    time_per_question: int, target_score: int, 
                                                    max_score: int, attempt_number: int, persona: str):
        """
        Generate question responses with learning curve
        Later attempts have more correct answers
        """
        # Create a list to track which questions should be correct
        question_correctness = []
        current_score = 0
        
        # Calculate target correct probability from target_score
        target_prob = target_score / max_score
        
        # For retry attempts (attempt > 1), ADD 20-30% more correct answers
        # This ensures score increases significantly
        if attempt_number > 1:
            # Add 25% to probability (guaranteed improvement)
            improvement = 0.25
            target_prob = min(0.98, target_prob + improvement)
            
            # Also boost the target_score itself to ensure higher actual score
            additional_points = int(max_score * improvement)
            target_score = min(max_score, target_score + additional_points)
        
        # First pass: Decide which questions should be correct based on probability
        for i, question in enumerate(quiz_questions):
            # Determine if this question should be correct
            # Use slightly randomized probability around target
            question_prob = target_prob + random.uniform(-0.03, 0.03)
            question_prob = max(0.0, min(1.0, question_prob))  # Clamp between 0-1
            
            should_be_correct = random.random() < question_prob
            question_correctness.append(should_be_correct)
            
            if should_be_correct:
                current_score += question['points']
        
        # Second pass: Adjust if we're too far from target score
        # This ensures we hit the target score more accurately
        score_diff = target_score - current_score
        
        if score_diff > 0:
            # Need to make some wrong answers correct
            wrong_indices = [i for i, correct in enumerate(question_correctness) if not correct]
            if wrong_indices:
                # Sort by points (prioritize high-value questions)
                wrong_indices.sort(key=lambda i: quiz_questions[i]['points'], reverse=True)
                
                for idx in wrong_indices:
                    if score_diff <= 0:
                        break
                    question_correctness[idx] = True
                    current_score += quiz_questions[idx]['points']
                    score_diff -= quiz_questions[idx]['points']
        elif score_diff < 0:
            # Need to make some correct answers wrong
            correct_indices = [i for i, correct in enumerate(question_correctness) if correct]
            if correct_indices:
                # Sort by points (remove low-value questions first)
                correct_indices.sort(key=lambda i: quiz_questions[i]['points'])
                
                for idx in correct_indices:
                    if score_diff >= 0:
                        break
                    question_correctness[idx] = False
                    current_score -= quiz_questions[idx]['points']
                    score_diff += quiz_questions[idx]['points']
        
        # Generate responses
        for i, question in enumerate(quiz_questions):
            question_id = question['id']
            is_correct = question_correctness[i]
            
            if is_correct:
                user_answer = question['correct_answer']
                points_earned = question['points']
            else:
                # Generate wrong answer
                wrong_answers = [
                    "Sai rồi", "Không chính xác", "Đáp án khác",
                    f"Option {random.choice(['A', 'B', 'C', 'D'])}"
                ]
                user_answer = random.choice(wrong_answers)
                points_earned = 0
            
            response_id = str(uuid.uuid4())
            answered_at = start_time + timedelta(seconds=i * time_per_question)
            
            self.cursor.execute("""
                INSERT INTO question_responses (id, attempt_id, question_id, user_answer,
                                                 is_correct, points_earned, time_spent_seconds, answered_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (response_id, attempt_id, question_id, user_answer, is_correct,
                  points_earned, time_per_question, answered_at))
            
            # Log quiz interaction flow (view -> hint? -> answer changes? -> submit)
            self._log_quiz_interaction_flow(user_id, attempt_id, question_id, answered_at, 
                                           user_answer, is_correct, time_per_question, persona)
        
        # Return actual score achieved
        return current_score
    
    def _log_quiz_interaction_flow(self, user_id: str, attempt_id: str, question_id: str,
                                   answered_at: datetime, final_answer: str, is_correct: bool,
                                   time_per_question: int, persona: str):
        """
        Log realistic quiz interaction flow for one question:
        1. view - user sees the question
        2. hint_request (optional) - user requests hint
        3. answer (one or more) - user selects/changes answer
        4. submit - user submits final answer
        """
        # Start from beginning of time allocated for this question
        question_start_time = answered_at - timedelta(seconds=time_per_question)
        current_time = question_start_time
        
        # 1. Always start with VIEW action
        self._insert_quiz_log(user_id, attempt_id, question_id, current_time, 
                             'view', None, None, 0, 0, False)
        
        # Determine hint probability based on persona and correctness
        if persona == PERSONA_DILIGENT:
            hint_prob = 0.15 if is_correct else 0.25  # Low probability, even when wrong
        elif persona == PERSONA_AVERAGE:
            hint_prob = 0.30 if is_correct else 0.45  # Moderate
        elif persona == PERSONA_STRUGGLING:
            hint_prob = 0.40 if is_correct else 0.60  # High probability
        else:  # DROPOUT
            hint_prob = 0.20  # Low effort
        
        hint_used = False
        answer_changes_count = 0
        
        # Simulate thinking time before first action (10-40% of total time)
        thinking_time = int(time_per_question * random.uniform(0.10, 0.40))
        current_time += timedelta(seconds=thinking_time)
        
        # 2. Optional: hint_request
        if random.random() < hint_prob:
            hint_used = True
            hint_time_spent = random.randint(2000, 8000)  # 2-8 seconds reading hint
            self._insert_quiz_log(user_id, attempt_id, question_id, current_time,
                                 'hint_request', None, None, hint_time_spent, 0, True)
            current_time += timedelta(milliseconds=hint_time_spent)
        
        # 3. Answer selection (with possible changes)
        # Determine if user will change answer (10-20% probability)
        will_change_answer = random.random() < 0.15
        
        if will_change_answer and not is_correct:
            # User initially picks wrong answer, then changes to correct/another
            answer_changes_count = random.randint(1, 2)
            
            # First wrong answer
            wrong_answers = ["Option A", "Option B", "Option C", "Option D"]
            first_answer = random.choice(wrong_answers)
            time_to_first = random.randint(3000, 15000)
            self._insert_quiz_log(user_id, attempt_id, question_id, current_time,
                                 'answer', first_answer, False, time_to_first, 
                                 answer_changes_count, hint_used)
            current_time += timedelta(milliseconds=time_to_first)
            
            # If 2 changes, add another wrong answer
            if answer_changes_count == 2:
                second_answer = random.choice([a for a in wrong_answers if a != first_answer])
                time_to_second = random.randint(5000, 20000)
                self._insert_quiz_log(user_id, attempt_id, question_id, current_time,
                                     'answer', second_answer, False, time_to_second,
                                     answer_changes_count, hint_used)
                current_time += timedelta(milliseconds=time_to_second)
            
            # Final answer (could be correct or wrong depending on is_correct)
            time_to_final = random.randint(3000, 12000)
            self._insert_quiz_log(user_id, attempt_id, question_id, current_time,
                                 'answer', final_answer, is_correct, time_to_final,
                                 answer_changes_count, hint_used)
            current_time += timedelta(milliseconds=time_to_final)
        else:
            # User picks answer directly (no change)
            time_to_answer = random.randint(5000, 30000)
            self._insert_quiz_log(user_id, attempt_id, question_id, current_time,
                                 'answer', final_answer, is_correct, time_to_answer,
                                 0, hint_used)
            current_time += timedelta(milliseconds=time_to_answer)
        
        # 4. Always end with SUBMIT action
        submit_delay = random.randint(1000, 3000)  # 1-3 seconds to click submit
        current_time += timedelta(milliseconds=submit_delay)
        self._insert_quiz_log(user_id, attempt_id, question_id, current_time,
                             'submit', final_answer, is_correct, submit_delay,
                             answer_changes_count, hint_used)
    
    def _insert_quiz_log(self, user_id: str, attempt_id: str, question_id: str,
                        timestamp: datetime, action_type: str, answer_given: str,
                        is_correct: bool, time_spent_ms: int, answer_changes_count: int,
                        hint_used: bool):
        """Insert a single quiz interaction log entry"""
        log_id = str(uuid.uuid4())
        
        metadata = {
            'action': action_type,
            'timestamp_iso': timestamp.isoformat()
        }
        
        self.cursor.execute("""
            INSERT INTO quiz_interaction_logs (id, user_id, attempt_id, question_id, timestamp,
                                                action_type, answer_given, is_correct, time_spent_ms,
                                                answer_changes_count, hint_used, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (log_id, user_id, attempt_id, question_id, timestamp, action_type,
              answer_given, is_correct, time_spent_ms, answer_changes_count, hint_used, Json(metadata)))
    
    def print_statistics(self):
        """Print data statistics"""
        print("\n" + "=" * 60)
        print("📊 THỐNG KÊ DỮ LIỆU ĐÃ TẠO")
        print("=" * 60)
        
        tables = [
            'profiles', 'user_roles', 'enrollments', 'user_sessions',
            'activity_logs', 'lesson_progress', 'quiz_attempts', 'question_responses',
            'quiz_interaction_logs', 'reading_behavior_logs', 'interaction_logs'
        ]
        
        for table in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = self.cursor.fetchone()[0]
            print(f"  {table:30s}: {count:6d} bản ghi")
        
        print("=" * 60)


def main():
    """Main function"""
    DB_CONFIG = {
        'host': os.getenv('LOCAL_DB_HOST', 'localhost'),
        'port': int(os.getenv('LOCAL_DB_PORT', 5432)),
        'database': os.getenv('LOCAL_DB_NAME', 'Lovable'),
        'user': os.getenv('LOCAL_DB_USER', 'postgres'),
        'password': os.getenv('LOCAL_DB_PASSWORD'),
        'schema': os.getenv('LOCAL_DB_SCHEMA', 'transform')
    }
    
    print("=" * 60)
    print(" TẠO DỮ LIỆU GIẢ LẬP HÀNH VI HỌC TẬP ".center(60, "="))
    print("=" * 60)
    print(f"Thời gian: {START_DATE.date()} đến {END_DATE.date()}")
    print(f"Số sinh viên: 20")
    print("=" * 60)
    
    generator = DataGenerator(DB_CONFIG)
    
    try:
        generator.connect()
        generator.clear_behavior_data()
        generator.load_existing_content()
        generator.generate_users(20)
        generator.generate_enrollments()
        generator.generate_learning_behavior()
        generator.print_statistics()
        
        print("\n✓ HOÀN THÀNH!\n")
        
    except Exception as e:
        print(f"\n✗ Lỗi: {e}")
        if generator.conn:
            generator.conn.rollback()
    finally:
        generator.disconnect()


if __name__ == '__main__':
    main()
