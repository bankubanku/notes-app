from flask import Blueprint, redirect, render_template, request, flash, url_for
from ..models import User
from .. import db, mail
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_mail import Message

auth = Blueprint("auth", __name__)

s = URLSafeTimedSerializer('secret-key', salt='confirm-email')


@auth.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                flash("Logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html")


@auth.route("/sign-up", methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if email_exists:
            flash('Email is already in use.', category='error')
        elif username_exists:
            flash('Username is already in use.', category='error')
        elif password1 != password2:
            flash('Password don\'t match!', category='error')
        elif len(username) < 3:
            flash('Username needs to have at least 3 characters.', category='error')
        elif len(password1) < 4:
            flash('Password needs to be at least 4 characters long.',
                  category='error')
        elif len(email) < 4:
            flash("Email is invalid.", category='error')
        else:
            creds = {"email": email, 
                    "username": username,
                    "password": password1}
            token = s.dumps(creds)

            msg = Message("Email verification",
                          sender='youremail', recipients=[email])
            link = url_for('auth.create_account', token=token, _external=True)
            msg.body = 'Clik this link to create your account {}'.format(link)
            mail.send(msg)

            # create_account(email, username, password1)
            # return redirect(url_for('views.home'))
    return render_template("sign_up.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))


@auth.route("/create-account/<token>", methods=['POST', 'GET'])
def create_account(token):
    try:
        creds = s.loads(token, max_age=3600)
        email = creds["email"]
        username = creds["username"]
        password = creds["password"]

        new_user = User(email=email, username=username,
                    password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user, remember=True)
        flash('User created!')
        return redirect(url_for('views.home'))

    except SignatureExpired:
        return redirect(url_for('auth.sign_up'))

