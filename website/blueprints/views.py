from crypt import methods
from distutils.log import error
from flask import Blueprint, redirect, render_template, request, flash, url_for
from flask_login import current_user, login_required
from .. import db
from ..models import Note


views = Blueprint("views", __name__)


@views.route('/home')
@views.route('/')
@login_required
def home():
    notes = current_user.notes
    return render_template('home.html', username=current_user.username, notes=notes)


@views.route('/test')
def test():
    return render_template('test.html')


@views.route('/create-note', methods=['POST', 'GET'])
@login_required
def create_note():
    if request.method == 'POST':
        title = request.form.get('title')
        note_content = request.form.get('note_content')

        if not note_content:
            flash('Note cannot be empty', category='error')
        else:
            if not title:
                title = "(No title)"
            note = Note(title=title, note_content=note_content,
                        author=current_user.id)
            db.session.add(note)
            db.session.commit()
            flash('Note added', category='success')
            return redirect(url_for('views.home'))

    return render_template('create_note.html')


@views.route('/edit-note/<id>', methods=['POST', 'GET'])
@login_required
def edit_note(id):
    note = Note.query.filter_by(id=id).first()
    
    if note.author != current_user.id:
        flash('You can edit only your notes', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        title = request.form.get('title')
        note_content = request.form.get('note_content')

        if note:
            if not note_content:
                flash('Note cannot be empty', category='error')
            else:
                if not title:
                    title = "(No title)"
                note.title = title
                note.note_content = note_content
                db.session.commit()
                flash('Note edited', category='success')
                return redirect(url_for('views.home'))
        else:
            flash("Note doesn't exist", category=error)
            
    return render_template('edit_note.html', note=note)


@views.route('/delete/<id>', methods=['POST', 'GET'])
@login_required
def delete(id):
    note = Note.query.filter_by(id=id).first()
    
    if note.author != current_user.id:
        flash('You can delete only your notes', category='error')
        return redirect(url_for('views.home'))

    if not note:
        flash("Note doesn't exist", category='error')
    else:
        db.session.delete(note)
        db.session.commit()
        flash('Post deleted', category='success')
    
    return redirect(url_for('views.home'))