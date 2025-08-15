from website import mysql

class College:
    __tablename__ = 'college'

    def __init__(self, id=None, college_name=None, college_code=None):
        self.id = id
        self.college_name = college_name
        self.college_code = college_code

    # ---------- CRUD METHODS ----------
    def insert(self):
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO college (college_name, college_code) VALUES (%s, %s)",
            (self.college_name, self.college_code)
        )
        mysql.connection.commit()
        cur.close()

    def update(self):
        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE college SET college_name=%s, college_code=%s WHERE id=%s",
            (self.college_name, self.college_code, self.id)
        )
        mysql.connection.commit()
        cur.close()

    def delete(self):
        cur = mysql.connection.cursor()
        try:
            # Unlink college from students
            cur.execute("UPDATE student SET college_id = NULL WHERE college_id = %s", (self.id,))
            # Unlink college from courses
            cur.execute("UPDATE course SET college_id = NULL WHERE college_id = %s", (self.id,))
            # Delete the college itself
            cur.execute("DELETE FROM college WHERE id = %s", (self.id,))
            mysql.connection.commit()
        except Exception:
            mysql.connection.rollback()
            raise
        finally:
            cur.close()

    # ---------- RETRIEVE METHODS ----------
    @classmethod
    def get_colleges(cls):
        cur = mysql.connection.cursor(dictionary=True)
        cur.execute(f"SELECT * FROM {cls.__tablename__} ORDER BY college_name ASC")
        rows = cur.fetchall()
        cur.close()
        return rows

    @classmethod
    def get_colleges_paginated(cls, offset, limit):
        cur = mysql.connection.cursor(dictionary=True)
        cur.execute(f"""
            SELECT * FROM {cls.__tablename__}
            ORDER BY id DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        rows = cur.fetchall()
        cur.close()
        return rows

    @classmethod
    def search_colleges(cls, query):
        cur = mysql.connection.cursor(dictionary=True)
        search_term = f"%{query}%"
        cur.execute(f"""
            SELECT * FROM {cls.__tablename__}
            WHERE college_name LIKE %s OR college_code LIKE %s
            ORDER BY college_name ASC
        """, (search_term, search_term))
        rows = cur.fetchall()
        cur.close()
        return rows

    # ---------- COUNT METHODS ----------
    @classmethod
    def count_colleges(cls):
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT COUNT(*) FROM {cls.__tablename__}")
        count = cur.fetchone()[0]
        cur.close()
        return count

    # ---------- UNIQUENESS CHECK ----------
    @classmethod
    def is_college_unique(cls, college_name, college_code, current_college_id=None):
        cur = mysql.connection.cursor()
        cur.execute(f"""
            SELECT id FROM {cls.__tablename__}
            WHERE (college_name = %s OR college_code = %s)
            AND (id != %s OR %s IS NULL)
        """, (college_name, college_code, current_college_id, current_college_id))
        result = cur.fetchone()
        cur.close()
        return result is None
