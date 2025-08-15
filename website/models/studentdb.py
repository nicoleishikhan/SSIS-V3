from website import mysql

class Student:
    __tablename__ = 'student'

    def __init__(self, id=None, student_id=None, first_name=None, last_name=None,
                 gender=None, year=None, course_id=None, college_id=None, cloudinary_url=None):
        self.id = id
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.year = year
        self.course_id = course_id
        self.college_id = college_id
        self.cloudinary_url = cloudinary_url

    # ---------- CRUD METHODS ----------
    def insert(self):
        cur = mysql.connection.cursor()
        cur.execute(f"""
            INSERT INTO {self.__tablename__} 
            (student_id, first_name, last_name, gender, year, course_id, college_id, cloudinary_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (self.student_id, self.first_name, self.last_name, self.gender, 
              self.year, self.course_id, self.college_id, self.cloudinary_url))
        mysql.connection.commit()
        cur.close()

    def update(self):
        cur = mysql.connection.cursor()
        cur.execute(f"""
            UPDATE {self.__tablename__} SET 
                student_id=%s, first_name=%s, last_name=%s, gender=%s, year=%s, 
                course_id=%s, college_id=%s, cloudinary_url=%s
            WHERE id=%s
        """, (self.student_id, self.first_name, self.last_name, self.gender,
              self.year, self.course_id, self.college_id, self.cloudinary_url, self.id))
        mysql.connection.commit()
        cur.close()

    def delete(self):
        cur = mysql.connection.cursor()
        cur.execute(f"DELETE FROM {self.__tablename__} WHERE id=%s", (self.id,))
        mysql.connection.commit()
        cur.close()

    # ---------- RETRIEVE METHODS ----------
    @classmethod
    def get_students(cls):
        cur = mysql.connection.cursor(dictionary=True)
        cur.execute(f"SELECT * FROM {cls.__tablename__} ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        return rows

    @classmethod
    def get_students_with_courses(cls, limit=None, offset=None):
        sql = f"""
            SELECT student.*, 
                CONCAT(
                    IFNULL(course.course_code, ''), 
                    ' (', 
                    IFNULL(college.college_name, ''), 
                    ')'
                ) AS course_college
            FROM student
            LEFT JOIN course ON student.course_id = course.id
            LEFT JOIN college ON student.college_id = college.id
            ORDER BY student.id DESC
        """
        params = ()
        if limit is not None and offset is not None:
            sql += " LIMIT %s OFFSET %s"
            params = (limit, offset)

        cur = mysql.connection.cursor(dictionary=True)
        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()
        return rows

    # ---------- COUNT METHODS ----------
    @classmethod
    def count_students(cls):
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT COUNT(*) FROM {cls.__tablename__}")
        count = cur.fetchone()[0]
        cur.close()
        return count

    # ---------- SEARCH ----------
    @classmethod
    def search_students(cls, query):
        search_term = f"%{query}%"
        cur = mysql.connection.cursor(dictionary=True)
        cur.execute(f"""
            SELECT student.*, 
                CONCAT(
                    IFNULL(course.course_code, ''), 
                    ' (', 
                    IFNULL(college.college_name, ''), 
                    ')'
                ) AS course_college
            FROM student
            LEFT JOIN course ON student.course_id = course.id
            LEFT JOIN college ON student.college_id = college.id
            WHERE student.student_id LIKE %s
            OR student.first_name LIKE %s
            OR student.last_name LIKE %s
            OR student.gender LIKE %s
            OR student.year LIKE %s
            OR course.course_code LIKE %s
            OR college.college_name LIKE %s
            ORDER BY student.id DESC
        """, (search_term, search_term, search_term, search_term, search_term,
            search_term, search_term))
        rows = cur.fetchall()
        cur.close()
        return rows

    # ---------- UNIQUENESS CHECK ----------
    @classmethod
    def is_student_unique(cls, student_id, first_name, last_name, gender, year, course_id, college_id, current_student_id=None):
        cur = mysql.connection.cursor()
        sql = f"""
            SELECT id FROM {cls.__tablename__}
            WHERE student_id=%s AND first_name=%s AND last_name=%s 
              AND gender=%s AND year=%s AND course_id=%s AND college_id=%s
        """
        params = (student_id, first_name, last_name, gender, year, course_id, college_id)

        if current_student_id:
            sql += " AND id != %s"
            params += (current_student_id,)

        cur.execute(sql, params)
        result = cur.fetchone()
        cur.close()
        return result is None

    # ---------- HELPER ----------
    @staticmethod
    def get_courses():
        cur = mysql.connection.cursor(dictionary=True)
        cur.execute("""
            SELECT course.id, course.course_code, course.college_id, college.college_name
            FROM course
            LEFT JOIN college ON course.college_id = college.id
            ORDER BY course.course_code ASC
        """)
        rows = cur.fetchall()
        cur.close()
        return rows
    
    @staticmethod
    def get_colleges():
        cur = mysql.connection.cursor(dictionary=True)
        cur.execute("SELECT id, college_name FROM college ORDER BY college_name ASC")
        rows = cur.fetchall()
        cur.close()
        return rows
    
    @staticmethod
    def get_student_by_id(student_id):
        cur = mysql.connection.cursor(dictionary=True)
        query = """
            SELECT s.id, s.student_id, s.first_name, s.last_name, s.gender, s.year,
                s.course_id, s.college_id, s.cloudinary_url
            FROM student s
            WHERE s.id = %s
        """
        cur.execute(query, (student_id,))
        student = cur.fetchone()
        cur.close()
        return student
