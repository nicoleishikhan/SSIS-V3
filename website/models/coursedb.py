from website import mysql

class Course:
    __tablename__ = 'course'

    def __init__(self, id=None, course_name=None, course_code=None, college_id=None):
        self.id = id
        self.course_name = course_name
        self.course_code = course_code
        self.college_id = college_id

    # ---------- CRUD METHODS ----------
    def insert(self):
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO course (course_name, course_code, college_id) VALUES (%s, %s, %s)",
            (self.course_name, self.course_code, self.college_id)
        )
        mysql.connection.commit()
        cur.close()

    def update(self):
        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE course SET course_name=%s, course_code=%s, college_id=%s WHERE id=%s",
            (self.course_name, self.course_code, self.college_id, self.id)
        )
        mysql.connection.commit()
        cur.close()

    def delete(self):
        cur = mysql.connection.cursor()
        # Unlink students from this course
        cur.execute("UPDATE student SET course_id = NULL WHERE course_id = %s", (self.id,))
        # Delete the course
        cur.execute("DELETE FROM course WHERE id = %s", (self.id,))
        mysql.connection.commit()
        cur.close()

    # ---------- RETRIEVE METHODS ----------
    @staticmethod
    def get_courses():
        cur = mysql.connection.cursor(dictionary=True)
        cur.execute("""
            SELECT course.*, college.college_code
            FROM course
            LEFT JOIN college ON course.college_id = college.id
            ORDER BY course_name ASC
        """)
        rows = cur.fetchall()
        cur.close()
        return rows

    @staticmethod
    def get_courses_paginated(offset, limit):
        cur = mysql.connection.cursor(dictionary=True)
        cur.execute("""
            SELECT course.*, college.college_code
            FROM course
            LEFT JOIN college ON course.college_id = college.id
            ORDER BY course_name ASC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        rows = cur.fetchall()
        cur.close()
        return rows

    @classmethod
    def get_courses_with_college(cls):
        cur = mysql.connection.cursor(dictionary=True)
        cur.execute(f"""
            SELECT course.*, college.college_name AS college_name, college.college_code AS college_code
            FROM {cls.__tablename__}
            LEFT JOIN college ON course.college_id = college.id
        """)
        rows = cur.fetchall()
        cur.close()
        return rows

    @classmethod
    def get_courses_with_college_paginated(cls, offset, limit):
        cur = mysql.connection.cursor(dictionary=True)
        cur.execute(f"""
            SELECT course.*, college.college_name AS college_name, college.college_code AS college_code
            FROM {cls.__tablename__}
            LEFT JOIN college ON course.college_id = college.id
            ORDER BY course.id DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        rows = cur.fetchall()
        cur.close()
        return rows

    @classmethod
    def get_colleges(cls):
        cur = mysql.connection.cursor(dictionary=True)
        cur.execute("SELECT id, college_name FROM college")
        rows = cur.fetchall()
        cur.close()
        return rows

    # ---------- SEARCH METHODS ----------
    @classmethod
    def search_courses(cls, query):
        cur = mysql.connection.cursor(dictionary=True)
        search_term = f"%{query}%"
        cur.execute(f"""
            SELECT course.*, college.college_code
            FROM {cls.__tablename__}
            LEFT JOIN college ON course.college_id = college.id
            WHERE course_name LIKE %s OR course_code LIKE %s OR college.college_code LIKE %s
        """, (search_term, search_term, search_term))
        rows = cur.fetchall()
        cur.close()
        return rows
    
    @classmethod
    def search_courses_with_college(cls, query):
        search_term = f"%{query}%"
        cur = mysql.connection.cursor(dictionary=True)
        cur.execute("""
            SELECT course.*, college.college_code
            FROM course
            LEFT JOIN college ON course.college_id = college.id
            WHERE course.course_name LIKE %s
            OR course.course_code LIKE %s
            OR college.college_code LIKE %s
            ORDER BY course.id DESC
        """, (search_term, search_term, search_term))
        rows = cur.fetchall()
        cur.close()
        return rows

    @staticmethod
    def search_courses_paginated(query, offset, limit):
        cur = mysql.connection.cursor(dictionary=True)
        search_term = f"%{query}%"
        cur.execute("""
            SELECT course.*, college.college_code
            FROM course
            LEFT JOIN college ON course.college_id = college.id
            WHERE course_name LIKE %s OR course_code LIKE %s
            ORDER BY course_name ASC
            LIMIT %s OFFSET %s
        """, (search_term, search_term, limit, offset))
        rows = cur.fetchall()
        cur.close()
        return rows

    # ---------- COUNT METHODS ----------
    @staticmethod
    def count_courses():
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM course")
        count = cur.fetchone()[0]
        cur.close()
        return count

    @staticmethod
    def count_courses_search(query):
        cur = mysql.connection.cursor()
        search_term = f"%{query}%"
        cur.execute("SELECT COUNT(*) FROM course WHERE course_name LIKE %s OR course_code LIKE %s",
                    (search_term, search_term))
        count = cur.fetchone()[0]
        cur.close()
        return count

    # ---------- UNIQUENESS CHECK ----------
    @classmethod
    def is_course_unique(cls, course_name, course_code, college_id):
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT id FROM course WHERE course_name = %s AND course_code = %s AND college_id = %s",
            (course_name, course_code, college_id)
        )
        result = cur.fetchone()
        cur.close()
        return result is None
