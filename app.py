from flask import render_template, request, Flask, redirect
import utils
from flask_sqlalchemy import SQLAlchemy
import os
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL')

db = SQLAlchemy(app)

@app.before_first_request
def before():
    db.create_all()

@app.route('/', methods=['POST', 'GET'])
def home():
    all = utils.Urls.query.all()
    rows = []
    for each in all:
        rows.append((each.id, each.long, each.short, each.visits))

    hosturl = request.host_url[8:] if request.host_url.startswith('https') else request.host_url[7:]
    if request.method=='POST':
        url_long = request.form['url']
        
        if not url_long.startswith('http'):
            url_long='http://'+url_long
        found_url = utils.Urls.query.filter_by(long=url_long).first()
        
        params = {'url_long':url_long, 'short':None, 'hosturl':hosturl, 'all':rows}
        if found_url:
            params['short'] = found_url.short
            return render_template('index.html', **params)
        else:
            url_short = ''
            while True:
                url_short = utils.shorten_url(url_long, len(hosturl))
                if not utils.Urls.query.filter_by(short=url_short).first():
                    break
            params['short'] = url_short
            new_url = utils.Urls(url_long, url_short)
            db.session.add(new_url)
            all = utils.Urls.query.all()
            rows = []
            for each in all:
                rows.append((each.id, each.long, each.short, each.visits))
            db.session.commit()
            params['all'] = rows
            return render_template('index.html', **params)
    
    return render_template('index.html', all=rows, hosturl=hosturl)

@app.route('/<short_url>')
def redirection(short_url):
    long_url = utils.Urls.query.filter_by(short=short_url).first()
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