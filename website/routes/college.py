from flask import Blueprint, render_template, request, flash, redirect, url_for
from ..models.collegedb import College

college = Blueprint('college', __name__)
college_model = College()

@college.route('/')
def college_home():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    total_colleges = College.count_colleges()
    total_pages = max(1, (total_colleges + per_page - 1) // per_page)
    offset = (page - 1) * per_page

    colleges = college_model.get_colleges_paginated(offset, per_page)
    return render_template("page-college.html", colleges=colleges, page=page, total_pages=total_pages)

@college.route('/add', methods=['GET', 'POST'])
def add_college():
    if request.method == 'POST':
        college_name = request.form.get('college_name')
        college_code = request.form.get('college_code')

        if not college_name or not college_code:
            flash('Name and code cannot be empty.', category='error')
        elif not College.is_college_unique(college_name, college_code):
            flash('College with the same name or code already exists.', category='error')
        else:
            College(college_name=college_name, college_code=college_code).insert()
            flash('College added.', category='success')
            return redirect(url_for('college.college_home'))

    return render_template('add-college.html')

@college.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_college(id):
    original_college = next((c for c in College.get_colleges() if c['id'] == id), None)
    if not original_college:
        flash('College not found.', category='error')
        return redirect(url_for('college.college_home'))

    if request.method == 'POST':
        college_name = request.form.get('college_name')
        college_code = request.form.get('college_code')

        if not college_name or not college_code:
            flash('Name and code cannot be empty.', category='error')
        elif not College.is_college_unique(college_name, college_code, current_college_id=id):
            flash('College with the same name or code already exists.', category='error')
        else:
            College(id=id, college_name=college_name, college_code=college_code).update()
            flash('College updated.', category='success')
            return redirect(url_for('college.college_home'))

    return render_template("edit-college.html", college=original_college)

@college.route('/delete/<int:id>', methods=['POST'])
def delete_college(id):
    College(id=id).delete()
    flash('College deleted. Students in this college will not be deleted.', category='success')
    return redirect(url_for('college.college_home'))

@college.route('/search', methods=['GET'])
def search_colleges():
    query = request.args.get('query', '').strip()
    if not query:
        return redirect(url_for('college.college_home'))

    colleges = college_model.search_colleges(query)

    if not colleges:
        flash('No results found.', category='info')

    # Optional: ensure college_name exists for template (if used in template)
    for c in colleges:
        c['college_name'] = c.get('college_name') or ''

    # Provide page variables for template
    page = 1
    total_pages = 1

    return render_template('page-college.html', colleges=colleges, page=page, total_pages=total_pages)
