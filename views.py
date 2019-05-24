import atexit
import json
import time
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from flask import render_template, request, flash, redirect
from flask_login import current_user, logout_user, login_user, login_required
from pony.orm import flush, select, db_session
from six.moves.urllib.request import urlopen

from app import app
from models import db


def print_date_time():
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))


def fetch_latest_version():
    print "trying to fetch latest version from github"
    try:
        app.config['release_info'] = json.loads(urlopen(app.config['release_url']).read())
        print "latest version:", app.config['release_info']['name']
    except:
        print "failed to fetch latest release data from github"


scheduler = BackgroundScheduler()
scheduler.add_job(func=print_date_time, trigger="interval", seconds=3)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


@app.route('/')
def index():
    users = db.User.select()
    return render_template('index.html', user=current_user, users=users, req=request)


@app.route('/ping')
def ping():
    return "pong"


@app.route('/fetch')
def fetch_version():
    fetch_latest_version()
    return app.config['release_info']['name']


@app.route('/version')
def version():
    print "data:", request.query_string
    id = request.args.get('node', default=0, type=int)
    ip = request.remote_addr
    version = request.args.get('version', default='1.1.1', type=str)

    db.VersionCheck(node=id, ip=ip, version=version, timestamp=datetime.now())
    flush()
    return "ok", 200


@app.route('/version/latest')
def latest_version():
    return app.config['release_info']['name'], 200


@app.route('/versions')
def versions():
    output = {}
    with db_session:
        version = request.args.get('version', default='latest', type=str)
        if version == 'all':
            checks = [{item.ip: item.version} for item in db.VersionCheck.select()]
        else:
            checks = [{item.ip: item.version} for item in select(c for c in db.VersionCheck if c.version == version)]
        output = {
            'checks': checks,
            'version': version
        }
    return json.dumps(output), 200


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        possible_user = db.User.get(login=username)
        if not possible_user:
            flash('Wrong username')
            return redirect('/login')
        if possible_user.password == password:
            possible_user.last_login = datetime.now()
            login_user(possible_user)
            return redirect('/')

        flash('Wrong password')
        return redirect('/login')
    else:
        return render_template('login.html')


@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        exist = db.User.get(login=username)
        if exist:
            flash('Username %s is already taken, choose another one' % username)
            return redirect('/reg')

        user = db.User(login=username, password=password)
        user.last_login = datetime.now()
        flush()
        login_user(user)
        flash('Successfully registered')
        return redirect('/')
    else:
        return render_template('reg.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out')
    return redirect('/')
