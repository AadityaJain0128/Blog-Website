from flask import Blueprint, render_template, redirect, request, flash, url_for, session
from .models import db, User
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from .email_otp import send_otp
from random import randint


auth = Blueprint("auth", __name__)


@auth.route("/signup", methods=['GET', 'POST'])
def sign_up():
    if current_user.is_authenticated:
        flash("You are already Logged In !", category="warning")
        return redirect("/")
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        firstName = request.form.get("firstName", "").strip()
        lastName = request.form.get("lastName", "").strip()
        emailID = request.form.get("emailID", "").strip()
        password1 = request.form.get("password1", "").strip()
        password2 = request.form.get("password2", "").strip()
        
        users = [row[0] for row in db.session.query(User.username).all()]
        user = User.query.filter_by(email=emailID).first()
        print(users)
        if username in users:
            flash("This username is not available !", "error")
            return render_template("sign-up.html", username=username, firstName=firstName, lastName=lastName, emailID=emailID, password1=password1, password2=password2)
        elif user:
            flash("E-Mail already exists !", category="error")
            return render_template("sign-up.html", username=username, firstName=firstName, lastName=lastName, emailID=emailID, password1=password1, password2=password2)
        elif len(username) < 3:
            flash("Username should have at least 3 characters !", category="error")
            return render_template("sign-up.html", username=username, firstName=firstName, lastName=lastName, emailID=emailID, password1=password1, password2=password2)
        elif len(firstName) < 2:
            flash("First Name should have at least 2 characters !", category="error")
            return render_template("sign-up.html", username=username, firstName=firstName, lastName=lastName, emailID=emailID, password1=password1, password2=password2)
        elif len(lastName) < 2:
            flash("Last Name should have at least 2 characters !", category="error")
            return render_template("sign-up.html", username=username, firstName=firstName, lastName=lastName, emailID=emailID, password1=password1, password2=password2)
        elif len(emailID) < 5:
            flash("E-Mail ID should have at least 5 characters !", category="error")
            return render_template("sign-up.html", username=username, firstName=firstName, lastName=lastName, emailID=emailID, password1=password1, password2=password2)
        elif len(password1) < 8:
            flash("Password should have at least 8 characters !", category="error")
            return render_template("sign-up.html", username=username, firstName=firstName, lastName=lastName, emailID=emailID, password1=password1, password2=password2)
        elif password1 != password2:
            flash("Passwords do not match !", category="error")
            return render_template("sign-up.html", username=username, firstName=firstName, lastName=lastName, emailID=emailID, password1=password1, password2=password2)
        else:
            session["username"] = username
            session["fname"] = firstName
            session["lname"] = lastName
            session["email"] = emailID
            session["password"] = password1
            return redirect(url_for("auth.verify"))
            
    return render_template("sign-up.html")


@auth.route("/verify", methods=['GET', 'POST'])
def verify():
    if current_user.is_authenticated:
        flash("You are already Logged In !", category="warning")
        return redirect("/")

    username = session.get("username", None)
    email = session.get("email", None)
    if not (username and email):
        flash("You can not access this page directly !", category="error")
        return redirect("/")
    
    if request.method == "POST":
        fname = session["fname"]
        lname = session["lname"]
        password = session["password"]
        user_otp = int(request.form.get("otp", 0))
        if session["otp"] == user_otp:
            user = User(username=username, fname=fname, lname=lname, email=email, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            session.clear()
            flash("Account Created Successfully !", category="success")
            return redirect(url_for("auth.login"))
        else:
            flash("Incorrect OTP !", category="error")

    else:
        if not session.get("otp", None):
            otp = randint(1000, 9999)
            session["otp"] = otp
            if send_otp(email, otp):
                flash("Please enter the OTP recieved on your E-Mail ID to proceed !", category="warning")
            else:
                flash("Some Error in creating your Account. Please try again later !", category="error")
                session.clear(otp)
                return redirect(url_for("auth.sign_up"))
        else:
            flash("Please do not reload this page !")
        return render_template("verify.html", emailID=email)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    next_page = request.args.get("next", "/")
    if current_user.is_authenticated:
        flash("You are already Logged In !", category="warning")
        return redirect(next_page)
    
    if request.method == "POST":
        if next_page == url_for("auth.logout"):
            next_page = "/"
        choice = request.form.get("choice")
        username = request.form.get("username", "")
        email = request.form.get("emailID", "")
        password = request.form.get("password", "")
        if choice == "username":
            user = User.query.filter_by(username=username).first()
        else:
            user = User.query.filter_by(email=email).first()

        if not user:
            flash("User does not exists with this credentials !", category="error")
            return render_template("login.html", username=username, password=password)
        
        
        if check_password_hash(user.password, password):
            flash("Login Successful !", category="success")
            login_user(user, remember=True)
            return redirect(next_page)
        else:
            flash("Incorrect Password !", category="error")
            return render_template("login.html", username=username, password=password)
    
    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have Logged Out !")
    return redirect(url_for("auth.login"))
