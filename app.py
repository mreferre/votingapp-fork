import os
import secrets

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS, cross_origin
from random import randrange
import simplejson as json
from multiprocessing import Pool
from multiprocessing import cpu_count

# Optional boto3 import for production with DynamoDB
try:
    import boto3
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    print("boto3 not available - running in development mode with mock data")

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(16))

# Simple password protection - in production, use proper authentication
VOTES_PASSWORD = os.getenv('VOTES_PASSWORD', 'votingapp2024')

cors = CORS(app, resources={r"/api/*": {"Access-Control-Allow-Origin": "*"}})

cpustressfactor = os.getenv('CPUSTRESSFACTOR', 1)
memstressfactor = os.getenv('MEMSTRESSFACTOR', 1)
ddb_aws_region = os.getenv('DDB_AWS_REGION')
ddb_table_name = os.getenv('DDB_TABLE_NAME', "votingapp-restaurants")

# Development mode with mock data
DEVELOPMENT_MODE = os.getenv('DEVELOPMENT_MODE', 'true').lower() == 'true' or not AWS_AVAILABLE

if DEVELOPMENT_MODE:
    print("Running in DEVELOPMENT MODE with mock data")
    # Mock data for development
    mock_votes = {
        'outback': 15,
        'bucadibeppo': 8,
        'ihop': 12,
        'chipotle': 23
    }
else:
    print("Running in PRODUCTION MODE with DynamoDB")
    try:
        ddb = boto3.resource('dynamodb', region_name=ddb_aws_region)
        ddbtable = ddb.Table(ddb_table_name)
    except Exception as e:
        print(f"Failed to connect to DynamoDB: {e}")
        print("Falling back to DEVELOPMENT MODE")
        DEVELOPMENT_MODE = True
        mock_votes = {
            'outback': 15,
            'bucadibeppo': 8,
            'ihop': 12,
            'chipotle': 23
        }

print("The cpustressfactor variable is set to: " + str(cpustressfactor))
print("The memstressfactor variable is set to: " + str(memstressfactor))
memeater=[]
memeater=[0 for i in range(10000)] 

## https://gist.github.com/tott/3895832
def f(x):
    for x in range(1000000 * int(cpustressfactor)):
        x*x

def readvote(restaurant):
    if DEVELOPMENT_MODE:
        return str(mock_votes.get(restaurant, 0))
    else:
        response = ddbtable.get_item(Key={'name': restaurant})
        # this is required to convert decimal to integer 
        normilized_response = json.dumps(response)
        json_response = json.loads(normilized_response)
        votes = json_response["Item"]["restaurantcount"]
        return str(votes)

def updatevote(restaurant, votes):
    if DEVELOPMENT_MODE:
        mock_votes[restaurant] = votes
        return str(votes)
    else:
        ddbtable.update_item(
            Key={
                'name': restaurant
            },
            UpdateExpression='SET restaurantcount = :value',
            ExpressionAttributeValues={
                ':value': votes
            },
            ReturnValues='UPDATED_NEW'
        )
        return str(votes)

def get_all_votes():
    """Helper function to get all restaurant votes"""
    restaurants = ["outback", "bucadibeppo", "ihop", "chipotle"]
    votes_data = []
    for restaurant in restaurants:
        votes = readvote(restaurant)
        votes_data.append({"name": restaurant, "votes": int(votes)})
    return votes_data

def check_auth():
    """Check if user is authenticated"""
    return session.get('authenticated', False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == VOTES_PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('votes'))
        else:
            return render_template('login.html', error='Invalid password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

@app.route('/votes')
def votes():
    if not check_auth():
        return redirect(url_for('login'))
    
    votes_data = get_all_votes()
    return render_template('votes.html', votes_data=votes_data)

@app.route('/api/vote', methods=['POST'])
def api_vote():
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 401
    
    restaurant = request.json.get('restaurant')
    if restaurant not in ["outback", "bucadibeppo", "ihop", "chipotle"]:
        return jsonify({'error': 'Invalid restaurant'}), 400
    
    string_votes = readvote(restaurant)
    votes = int(string_votes)
    votes += 1
    string_new_votes = updatevote(restaurant, votes)
    
    return jsonify({'restaurant': restaurant, 'votes': int(string_new_votes)})

@app.route('/')
def home():
    return """
    <h1>Welcome to the Voting App</h1>
    <p><b>Web Interface:</b></p>
    <p><a href="/votes" style="color: #667eea; text-decoration: none; font-weight: bold;">🍽️ Restaurant Voting Dashboard</a> (Password protected)</p>
    <br>
    <p><b>To vote via API, you can call the following endpoints:</b></p>
    <p>/api/outback</p>
    <p>/api/bucadibeppo</p>
    <p>/api/ihop</p>
    <p>/api/chipotle</p>
    <p><b>To query the votes via API:</b></p>
    <p>/api/getvotes</p>
    <p>/api/getheavyvotes (this generates artificial CPU/memory load)</p>
    """

@app.route("/api/outback")
def outback():
    string_votes = readvote("outback")
    votes = int(string_votes)
    votes += 1
    string_new_votes = updatevote("outback", votes)
    return string_new_votes 

@app.route("/api/bucadibeppo")
def bucadibeppo():
    string_votes = readvote("bucadibeppo")
    votes = int(string_votes)
    votes += 1
    string_new_votes = updatevote("bucadibeppo", votes)
    return string_new_votes 

@app.route("/api/ihop")
def ihop():
    string_votes = readvote("ihop")
    votes = int(string_votes)
    votes += 1
    string_new_votes = updatevote("ihop", votes)
    return string_new_votes 

@app.route("/api/chipotle")
def chipotle():
    string_votes = readvote("chipotle")
    votes = int(string_votes)
    votes += 1
    string_new_votes = updatevote("chipotle", votes)
    return string_new_votes 

@app.route("/api/getvotes")
def getvotes():
    string_outback = readvote("outback")
    string_ihop = readvote("ihop")
    string_bucadibeppo = readvote("bucadibeppo")
    string_chipotle = readvote("chipotle")
    string_votes = '[{"name": "outback", "value": ' + string_outback + '},' + '{"name": "bucadibeppo", "value": ' + string_bucadibeppo + '},' + '{"name": "ihop", "value": '  + string_ihop + '}, ' + '{"name": "chipotle", "value": '  + string_chipotle + '}]'
    return string_votes

@app.route("/api/getheavyvotes")
def getheavyvotes():
    string_outback = readvote("outback")
    string_ihop = readvote("ihop")
    string_bucadibeppo = readvote("bucadibeppo")
    string_chipotle = readvote("chipotle")
    string_votes = '[{"name": "outback", "value": ' + string_outback + '},' + '{"name": "bucadibeppo", "value": ' + string_bucadibeppo + '},' + '{"name": "ihop", "value": '  + string_ihop + '}, ' + '{"name": "chipotle", "value": '  + string_chipotle + '}]'
    print("You invoked the getheavyvotes API. I am eating 100MB * " + str(memstressfactor) + " at every votes request")
    memeater[randrange(10000)] = bytearray(1024 * 1024 * 100 * memstressfactor, encoding='utf8') # eats 100MB * memstressfactor
    print("You invoked the getheavyvotes API. I am eating some cpu * " + str(cpustressfactor) + " at every votes request")
    processes = cpu_count()
    pool = Pool(processes)
    pool.map(f, range(processes))
    return string_votes

if __name__ == '__main__':
   app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))
   app.debug =True
