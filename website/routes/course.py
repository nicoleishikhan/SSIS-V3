from flask import Blueprint, render_template, request, flash, redirect, url_for
from ..models.coursedb import Course

course = Blueprint('course', __name__)
course_model = Course()

@course.route('/')
def course_home():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    total_courses = Course.count_courses()
    total_pages = max(1, (total_courses + per_page - 1) // per_page)
    offset = (page - 1) * per_page

    courses = course_model.get_courses_with_college_paginated(offset, per_page)
    return render_template("page-course.html", courses=courses, page=page, total_pages=total_pages)

@course.route('/add', methods=['GET', 'POST'])
def add_course():
    colleges = Course.get_colleges()

    if request.method == 'POST':
        course_name = request.form.get('course_name')
        course_code = request.form.get('course_code')
        college_id = request.form.get('college')

        if not course_name or not course_code or not college_id:
            flash('All fields are required.', category='error')
        elif not Course.is_course_unique(course_name, course_code, college_id):
            flash('Course with the same name or code already exists for this college.', category='error')
        else:
            Course(course_name=course_name, course_code=course_code, college_id=college_id).insert()
            flash('Course added.', category='success')
            return redirect(url_for('course.course_home'))

    return render_template("add-course.html", colleges=colleges)

@course.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_course(id):
    original_course = next((c for c in Course.get_courses_with_college() if c['id'] == id), None)
    if not original_course:
        flash('Course not found.', category='error')
        return redirect(url_for('course.course_home'))

    colleges = Course.get_colleges()

    if request.method == 'POST':
        course_name = request.form.get('course_name')
        course_code = request.form.get('course_code')
        college_id = request.form.get('college')

        if not course_name or not course_code or not college_id:
            flash('All fields are required.', category='error')
        elif not Course.is_course_unique(course_name, course_code, college_id):
            flash('Course with the same name or code already exists for this college.', category='error')
        else:
            Course(id=id, course_name=course_name, course_code=course_code, college_id=college_id).update()
            flash('Course updated.', category='success')
            return redirect(url_for('course.course_home'))

    return render_template("edit-course.html", course=original_course, colleges=colleges)

@course.route('/delete/<int:id>', methods=['POST'])
def delete_course(id):
    Course(id=id).delete()
    flash('Course deleted. Students in this course will not be deleted.', category='success')
    return redirect(url_for('course.course_home'))

@course.route('/search', methods=['GET'])
def search_course():
    query = request.args.get('query', '').strip()
    if not query:
        return redirect(url_for('course.course_home'))

    courses = Course.search_courses_with_college(query)

    if not courses:
        flash('No results found.', category='info')

    # Ensure college_name exists for template
    for c in courses:
        c['college_name'] = c.get('college_name') or ''

    # Define page variables for template
    page = 1
    total_pages = 1

    return render_template('page-course.html', courses=courses, page=page, total_pages=total_pages)