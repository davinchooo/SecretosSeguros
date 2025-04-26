from flask import render_template, redirect, url_for, session
from app import app


# app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    return render_template('form.html')

@app.route('/login', methods=["GET"])
def login():
    return render_template("login.html")

@app.route('/secrets', methods=["GET"])
def secrets():
    return render_template("secrets.html")

@app.route('/logout', methods=["GET"])
def logout():
    return render_template("logout.html")