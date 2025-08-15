from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from ..models.studentdb import Student
import cloudinary
import cloudinary.uploader

MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

student = Blueprint('student', __name__)
student_model = Student()


@student.route('/')
def student_home():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total_students = student_model.count_students()
    total_pages = max(1, (total_students + per_page - 1) // per_page)
    offset = (page - 1) * per_page
    students = student_model.get_students_with_courses(limit=per_page, offset=offset)

    # Ensure each student has a college name for display
    for s in students:
        s['college_name'] = s.get('college_name') or ''

    return render_template("page-student.html", students=students, page=page, total_pages=total_pages)


@student.route('/search')
def search_student():
    query = request.args.get('query', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10

    if not query:
        return redirect(url_for('student.student_home'))

    all_results = Student.search_students(query)
    total_students = len(all_results)
    total_pages = max(1, (total_students + per_page - 1) // per_page)
    offset = (page - 1) * per_page
    students = all_results[offset:offset + per_page]

    for s in students:
        s['college_name'] = s.get('college_name') or ''

    return render_template("page-student.html", students=students, page=page, total_pages=total_pages)


@student.route('/add', methods=['GET', 'POST'])
def add_student():
    courses = Student.get_courses()

    if request.method == 'POST':
        student_id = request.form.get('student_id')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        gender = request.form.get('gender')
        year = request.form.get('year')
        course_id = request.form.get('course_college') or None
        college_id = None

        # Get the college_id based on selected course
        if course_id:
            for c in courses:
                if str(c['id']) == course_id:
                    college_id = c['college_id']
                    break

        if not student_id or not first_name or not last_name or not gender or not year or not course_id:
            flash('All fields are required.', category='error')
        elif not Student.is_student_unique(student_id, first_name, last_name, gender, year, course_id, college_id):
            flash('Student with the same ID already exists.', category='error')
        else:
            try:
                cloudinary_url = ''
                uploaded_file = request.files.get('student_photo')
                if uploaded_file and uploaded_file.filename != '':
                    if allowed_file(uploaded_file.filename):
                        uploaded_file.seek(0, 2)
                        file_size = uploaded_file.tell()
                        uploaded_file.seek(0)
                        if file_size > MAX_FILE_SIZE:
                            flash('File exceeds 1MB limit.', category='error')
                            return redirect(url_for('student.add_student'))

                        response = cloudinary.uploader.upload(
                            uploaded_file,
                            folder=current_app.config['CLOUDY_FOLDER']
                        )
                        cloudinary_url = response.get('secure_url', '')
                    else:
                        flash('Invalid file type. Allowed: jpg, jpeg, png.', category='error')
                        return redirect(url_for('student.add_student'))

                Student(student_id=student_id, first_name=first_name, last_name=last_name,
                        gender=gender, year=year, course_id=course_id, college_id=college_id,
                        cloudinary_url=cloudinary_url).insert()
                flash('Student added.', category='success')
                return redirect(url_for('student.student_home'))
            except Exception as e:
                print(f"Error adding student: {e}")
                flash('Error adding student.', category='error')

    return render_template("add-student.html", courses=courses)


@student.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    courses = Student.get_courses()
    student = Student.get_student_by_id(id)
    if not student:
        flash('Student not found.', category='error')
        return redirect(url_for('student.student_home'))

    if request.method == 'POST':
        student_id = request.form.get('student_id')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        gender = request.form.get('gender')
        year = request.form.get('year')
        course_id = request.form.get('course_college') or None
        college_id = None

        if course_id:
            for c in courses:
                if str(c['id']) == course_id:
                    college_id = c['college_id']
                    break

        if not student_id or not first_name or not last_name or not gender or not year or not course_id:
            flash('All fields are required.', category='error')
        elif not Student.is_student_unique(student_id, first_name, last_name, gender, year, course_id, college_id, current_student_id=id):
            flash('Student with the same ID already exists.', category='error')
        else:
            try:
                cloudinary_url = student['cloudinary_url']
                uploaded_file = request.files.get('student_photo')
                if uploaded_file and uploaded_file.filename != '':
                    if allowed_file(uploaded_file.filename):
                        uploaded_file.seek(0, 2)
                        file_size = uploaded_file.tell()
                        uploaded_file.seek(0)
                        if file_size > MAX_FILE_SIZE:
                            flash('File exceeds 1MB limit.', category='error')
                            return redirect(url_for('student.edit_student', id=id))

                        response = cloudinary.uploader.upload(
                            uploaded_file,
                            folder=current_app.config['CLOUDY_FOLDER']
                        )
                        cloudinary_url = response.get('secure_url', '')
                    else:
                        flash('Invalid file type. Allowed: jpg, jpeg, png.', category='error')
                        return redirect(url_for('student.edit_student', id=id))

                Student(id=id, student_id=student_id, first_name=first_name, last_name=last_name,
                        gender=gender, year=year, course_id=course_id, college_id=college_id,
                        cloudinary_url=cloudinary_url).update()
                flash('Student updated.', category='success')
                return redirect(url_for('student.student_home'))
            except Exception as e:
                print(f"Error updating student: {e}")
                flash('Error updating student.', category='error')

    return render_template("edit-student.html", student=student, courses=courses)


@student.route('/delete/<int:id>', methods=['POST'])
def delete_student(id):
    Student(id=id).delete()
    flash('Student deleted.', category='success')
    return redirect(url_for('student.student_home'))
