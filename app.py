from flask import render_template, request, Flask, redirect
from flask_sqlalchemy import SQLAlchemy
import os
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

import string
import random

def shorten_url(long : str, host_len : int)->str:
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    short = ''.join(random.choices(letters, k=20-host_len))
    return short

class Urls(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    long = db.Column("long", db.String())
    short = db.Column("short", db.String(20))
    visits = db.Column("visits", db.Integer)

    def __init__(self, long, short):
        self.long = long
        self.short = short
        self.visits = 0

@app.before_first_request
def before():
    db.create_all()

@app.route('/', methods=['POST', 'GET'])
def home():
    all =  Urls.query.all()
    rows = []
    for each in all:
        rows.append((each.id, each.long, each.short, each.visits))

    hosturl = request.host_url[8:] if request.host_url.startswith('https') else request.host_url[7:]
    if request.method=='POST':
        url_long = request.form['url']
        
        if not url_long.startswith('http'):
            url_long='http://'+url_long
        found_url =  Urls.query.filter_by(long=url_long).first()
        
        params = {'url_long':url_long, 'short':None, 'hosturl':hosturl, 'all':rows}
        if found_url:
            params['short'] = found_url.short
            return render_template('index.html', **params)
        else:
            url_short = ''
            while True:
                url_short =  shorten_url(url_long, len(hosturl))
                if not  Urls.query.filter_by(short=url_short).first():
                    break
            params['short'] = url_short
            new_url =  Urls(url_long, url_short)
            db.session.add(new_url)
            all =  Urls.query.all()
            rows = []
            for each in all:
                rows.append((each.id, each.long, each.short, each.visits))
            db.session.commit()
            params['all'] = rows
            return render_template('index.html', **params)
    
    return render_template('index.html', all=rows, hosturl=hosturl)

@app.route('/<short_url>')
def redirection(short_url):
    long_url =  Urls.query.filter_by(short=short_url).first()
    if long_url:
        long_url.visits += 1
        db.session.commit()
        return redirect(long_url.long)
    else:
        return f'<h1>Url doesnt exist</h1>'

def main():
    
    app.run(port=5050)

if __name__=='__main__':
    main()