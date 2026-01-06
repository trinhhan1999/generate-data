import json
import psycopg2
from psycopg2.extras import Json
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PostgresImporter:
    """Import JSON data into PostgreSQL database"""
    
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                host=self.db_config.get('host'),
                port=self.db_config.get('port'),
                database=self.db_config.get('database'),
                user=self.db_config.get('user'),
                password=self.db_config.get('password')
            )
            self.cursor = self.conn.cursor()
            
            # Set search_path to use specified schema
            schema = self.db_config.get('schema', 'public')
            self.cursor.execute(f"SET search_path TO {schema}, public")
            self.conn.commit()
            
            print(f"✓ Kết nối database thành công! (Schema: {schema})")
        except Exception as e:
            print(f"✗ Lỗi kết nối database: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("✓ Đã đóng kết nối database")
    
    def load_json_file(self, file_path: str) -> Dict:
        """Load JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✓ Đã đọc file JSON: {file_path}")
            return data
        except Exception as e:
            print(f"✗ Lỗi đọc file JSON: {e}")
            raise
    
    def create_schema(self, schema_file: str = 'create_schema.sql'):
        """Execute schema creation SQL file"""
        try:
            schema = self.db_config.get('schema', 'public')
            if schema != 'public':
                self.cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
                self.cursor.execute(f"SET search_path TO {schema}, public")
                self.conn.commit()
                print(f"✓ Đã tạo/sử dụng schema: {schema}")
            
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            self.cursor.execute(schema_sql)
            self.conn.commit()
            print("✓ Đã tạo các bảng thành công!")
        except Exception as e:
            print(f"✗ Lỗi tạo schema: {e}")
            self.conn.rollback()
            raise
    
    def insert_data(self, table_name: str, records: List[Dict[str, Any]]):
        """Insert data into a table"""
        if not records:
            print(f"  → Bảng {table_name}: Không có dữ liệu")
            return
        
        try:
            columns = list(records[0].keys())
            placeholders = ', '.join(['%s'] * len(columns))
            columns_str = ', '.join(columns)
            
            query = f"""
                INSERT INTO {table_name} ({columns_str})
                VALUES ({placeholders})
                ON CONFLICT (id) DO NOTHING
            """
            
            inserted_count = 0
            for record in records:
                values = []
                for col in columns:
                    value = record.get(col)
                    if isinstance(value, (dict, list)):
                        value = Json(value)
                    values.append(value)
                
                self.cursor.execute(query, values)
                inserted_count += 1
            
            self.conn.commit()
            print(f"  ✓ Bảng {table_name}: Đã insert {inserted_count}/{len(records)} bản ghi")
            
        except Exception as e:
            print(f"  ✗ Lỗi insert vào bảng {table_name}: {e}")
            self.conn.rollback()
            raise
    
    def import_all_tables(self, json_data: Dict):
        """Import all tables from JSON data"""
        table_order = [
            'profiles', 'user_roles', 'courses', 'modules', 'lessons',
            'enrollments', 'forum_posts', 'forum_reactions', 'user_sessions',
            'activity_logs', 'interaction_logs', 'lesson_progress', 'quizzes',
            'questions', 'quiz_attempts', 'question_responses',
            'quiz_interaction_logs', 'reading_behavior_logs'
        ]
        
        tables_data = json_data.get('tables', {})
        
        print("\n🚀 Bắt đầu import dữ liệu...")
        print(f"   Tổng số bảng: {len(table_order)}")
        print("-" * 60)
        
        for table_name in table_order:
            records = tables_data.get(table_name, [])
            self.insert_data(table_name, records)
        
        print("-" * 60)
        print("✓ Hoàn thành import tất cả dữ liệu!\n")
    
    def get_table_counts(self):
        """Get row counts for all tables"""
        table_names = [
            'profiles', 'user_roles', 'courses', 'modules', 'lessons',
            'enrollments', 'forum_posts', 'forum_reactions', 'user_sessions',
            'activity_logs', 'interaction_logs', 'lesson_progress', 'quizzes',
            'questions', 'quiz_attempts', 'question_responses',
            'quiz_interaction_logs', 'reading_behavior_logs'
        ]
        
        print("\n📊 Thống kê số lượng bản ghi:")
        print("-" * 60)
        
        for table_name in table_names:
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = self.cursor.fetchone()[0]
                print(f"   {table_name:30s}: {count:5d} bản ghi")
            except Exception as e:
                print(f"   {table_name:30s}: Lỗi - {e}")
        
        print("-" * 60)


def main():
    """Main execution function"""
    
    # Đọc cấu hình từ file .env
    DB_CONFIG = {
        'host': os.getenv('LOCAL_DB_HOST', 'localhost'),
        'port': int(os.getenv('LOCAL_DB_PORT', 5432)),
        'database': os.getenv('LOCAL_DB_NAME', 'Lovable'),
        'user': os.getenv('LOCAL_DB_USER', 'postgres'),
        'password': os.getenv('LOCAL_DB_PASSWORD'),
        'schema': os.getenv('LOCAL_DB_SCHEMA', 'transform')
    }
    
    JSON_FILE = 'database-export-2026-01-02.json'
    SCHEMA_FILE = 'create_schema.sql'
    
    if not os.path.exists(JSON_FILE):
        print(f"✗ Không tìm thấy file: {JSON_FILE}")
        return
    
    if not os.path.exists(SCHEMA_FILE):
        print(f"✗ Không tìm thấy file: {SCHEMA_FILE}")
        return
    
    print("=" * 60)
    print(" IMPORT DỮ LIỆU VÀO POSTGRESQL ".center(60, "="))
    print("=" * 60)
    
    importer = None
    try:
        # 1. Khởi tạo và kết nối
        importer = PostgresImporter(DB_CONFIG)
        importer.connect()
        
        # 2. Tạo schema (các bảng)
        print("\n📋 Tạo schema database...")
        importer.create_schema(SCHEMA_FILE)
        
        # 3. Đọc dữ liệu JSON
        print("\n📂 Đọc dữ liệu từ file JSON...")
        json_data = importer.load_json_file(JSON_FILE)
        
        # 4. Import dữ liệu
        importer.import_all_tables(json_data)
        
        # 5. Thống kê
        importer.get_table_counts()
        
        print("\n" + "=" * 60)
        print("✓ HOÀN THÀNH!".center(60))
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Có lỗi xảy ra: {e}")
        
    finally:
        if importer:
            importer.disconnect()


if __name__ == '__main__':
    main()
