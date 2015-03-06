# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
from contextlib import closing
import os
import json
from rq import Queue
from rq.job import Job
from worker import conn
import random
import ast
from codecs import encode
import collections


app = Flask(__name__)
q = Queue(connection=conn)
# Set up appropriate app settings 
#app.config.from_object(os.environ['APP_SETTINGS'])
#print(os.environ['APP_SETTINGS'])

# configuration
DATABASE = os.path.join(app.root_path, 'showcase.db')
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/',  methods=['GET', 'POST'])
def show_entries():
    #db = get_db()
    #cur = g.db.execute('select title, text from entries order by id desc')
    #entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    #return render_template('show_entries.html', entries=entries)
    return render_template('index.html')

def count_and_save_words(url):
    print url
    print 'count and save words'

@app.route('/start', methods=['POST'])
def get_counts():
    data = json.loads(request.data.decode())
    url = data["url"]
    # form URL, id necessary
    if 'http://' not in url[:7]:
        url = 'http://' + url
    # start job
    job = q.enqueue_call(
        func=count_and_save_words, args=(url,), result_ttl=5000
    )
    # return created job id
    return job.get_id()

class NoLineupFoundException(Exception):
    status_code = 400
    def __init__(self, details=None):
        Exception.__init__(self)
        self.message = "No showcase lineups were found that satisfy the conditions." + \
            " Please increase the maximum number of conflicts allowed."
        self.details = details
    
@app.errorhandler(NoLineupFoundException)
def bad_request_handler(error):
    return bad_request(error.message)

def bad_request(message):
    response = jsonify({'message': message})
    response.status_code = 404
    return response

@app.route('/upload', methods=['POST'])
def upload():
    data = json.loads(request.data.decode())
    fixed_teams = data["fixed_teams"]
    dance_teams = data["result"]
    max_conflicts = int(data["max_conflicts"])
    print dance_teams
    # form URL, id necessary
    
    #job = q.enqueue_call(
    #    func=count_and_save_words, args=(dance_teams,), result_ttl=5000
    #)
    # return created job id
    fixed = convertToDict(fixed_teams)
    dance_teams = convertToDict(dance_teams)
    fixed_teams = {}
    for key, value in fixed.items():
        fixed_teams[int(key)] = value

    for team, dancers in dance_teams.items():
        dance_teams[team] = [dancer.lower() for dancer in dancers]

    showcaseOrders = []
    orders = []
    for i in range(6):
        order = findShowcaseOrder(fixed_teams, dance_teams, max_conflicts)
        print 'order', order
        order_with_conflicts = []
        if not order or not isOrderUnique(order, orders):
            continue
        for i in range(len(order) - 1):
            curr_team = dance_teams[order[i]]
            next_team = dance_teams[order[i+1]]
            conflicts = list(numConflicts(curr_team, next_team))
            order_with_conflicts.append((order[i], conflicts))
        order_with_conflicts.append((order[-1], []))
        showcaseOrders.append(order_with_conflicts)
        orders.append(order)
    if len(showcaseOrders) == 0:
         raise NoLineupFoundException()
    return jsonify(orders=showcaseOrders)

def isOrderUnique(showcase_order, orders):
    for order in orders:
        if sameOrder(showcase_order, order):
            return False
    return True

def sameOrder(order1, order2):
    for i in range(len(order1)):
        if order1[i] != order2[i]:
            return False
    return True


def numConflicts(team1, team2):
    team11 = set(team1)
    team22 = set(team2)
    conflicts = team11.intersection(team22)
    return conflicts

def reverseDict(dic):
    new_dict = {}
    for key,values in dic.items():
        new_dict[values] = key.lower()
    return new_dict

def convertToDict(data): # currently dictionary contains unicode characters
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convertToDict, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convertToDict, data))
    else:
        return data

def findShowcaseOrder(fixed_teams, dance_teams, max_conflicts):
    teams = dance_teams['teams']
    teams = teams[:]
    random.shuffle(teams)
    for index, team in fixed_teams.items():
        teams.remove(team)
    DANCE_TEAMS = dance_teams
    return findOrder(0, teams, None, fixed_teams, DANCE_TEAMS, max_conflicts)



def findOrder(index, teams, prev_team, fixed_teams, DANCE_TEAMS, MAX_CONFLICTS):
    if len(teams) == 0:
        return []
    if index in fixed_teams:
        if index == 0:
            conflicts = 0
        else:
            team1 = DANCE_TEAMS[prev_team]
            team2 = DANCE_TEAMS[fixed_teams[index]]
            conflicts = len(numConflicts(team1, team2))
        if conflicts <= MAX_CONFLICTS:
            order = findOrder(index+1, teams, fixed_teams[index], fixed_teams, DANCE_TEAMS, MAX_CONFLICTS - conflicts)
        else: 
            return False
        if order == False:
            return False
        return [fixed_teams[index]] + order
    for team in teams:
        if prev_team == None:
            teams_copy = teams[:]
            teams_copy.remove(team)
            order = findOrder(index+1, teams_copy, team, fixed_teams, DANCE_TEAMS, MAX_CONFLICTS)
            if order == False:
                continue
            else:
                return [team] + order
        else:
            team1 = DANCE_TEAMS[prev_team]
            team2 = DANCE_TEAMS[team]
            conflicts = len(numConflicts(team1, team2))
            if conflicts <= MAX_CONFLICTS:
                teams_copy = teams[:]
                teams_copy.remove(team)
                order = findOrder(index+1, teams_copy, team, fixed_teams, DANCE_TEAMS, MAX_CONFLICTS - conflicts)
                if order == False:
                    continue
                else:
                    return [team] + order
    return False
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()