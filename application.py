from flask import Flask, render_template, request, redirect
from flask import url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import time

app = Flask(__name__)
app.secret_key = 'super secret key'

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"


engine = create_engine('sqlite:///categoryitemwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# create a state token to prevent request forgery.
# store it in the session for later validation
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# add a logout function that calls gdisconnect and redirect to homepage
@app.route('/logout')
def logout():
    gdisconnect()
    flash('Successfully logged out!')
    return redirect(url_for('homepage'))


#gconnect code from Udacity course material
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # if user does not exist, create a new user
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '  # noqa
    flash("you are now logged in as %s" % login_session['username'])
    return output


# user functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
        'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# gdisconnect code from Udacity course material
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# jsonify categories and its items
@app.route('/catalog.json')
def catalogJSON():
    categories = session.query(Category).all()
    category_data = []
    for i in categories:
        data = i.serialize
        items = session.query(Item).filter_by(category_id=i.id).all()
        items_data = [j.serialize for j in items]
        data['item'] = items_data
        category_data.append(data)
    return jsonify(Category=category_data)


# homepage
@app.route('/')
@app.route('/catalog/')
def homepage():
    categories = session.query(Category).all()
    items = session.query(Item).order_by(desc(Item.timestamp)).limit(10).all()
    # if logged in, show add_item button, otherwise hide add_item button
    if 'username' not in login_session:
        return render_template('public_homepage.html',
                               categories=categories, items=items)
    else:
        return render_template('homepage.html',
                               categories=categories, items=items)


# show items for a specific category
@app.route('/catalog/<category_name>/items/')
def specificCategory(category_name):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=category.id)
    num = session.query(Item).filter_by(category_id=category.id).count()
    if 'username' not in login_session:
        return render_template('public_specific_category.html',
                               categories=categories, category=category,
                               items=items, num=num)
    else:
        return render_template('specific_category.html',
                               categories=categories, category=category,
                               items=items, num=num)


# show item
@app.route('/catalog/<category_name>/<item_title>/')
def specificItem(category_name, item_title):
    item = session.query(Item).filter_by(title=item_title).one()
    # If not logged in or user is not the creator, hide edit and delete button
    creator = getUserInfo(item.user_id)
    if 'username' not in login_session:
        return render_template('public_specific_item.html', item=item)
    elif creator.id != login_session['user_id']:
        return render_template('user_specific_item.html', item=item)
    else:
        return render_template('creator_specific_item.html', item=item)


# create route for newItem funcion here
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        newItem = Item(
            title=request.form['title'],
            category_id=session.query(Category).filter_by(
                name=request.form['category_name']).one().id,
            description=request.form['description'],
            user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash("new item created!")
        return redirect('/')
    else:
        return render_template(
            'newitem.html', categories=session.query(Category).all())


# create route for editItem function here
@app.route('/catalog/<item_title>/edit/', methods=['GET', 'POST'])
def editItem(item_title):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Item).filter_by(title=item_title).one()
    # alert user just in case the user tries to visit a url
    # that they are not authorized to access
    if editedItem.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this item. Please create your own item in order to delete.');}</script><body onload='myFunction()'>"  # noqa
    if request.method == 'POST':
        if request.form['title']:
            editedItem.title = request.form['title']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category_name']:
            editedItem.category_id = session.query(Category).filter_by(
                name=request.form['category_name']).one().id
        session.add(editedItem)
        session.commit()
        flash("item editted!")
        return redirect(url_for(
            'specificItem', category_name=editedItem.category.name,
            item_title=editedItem.title))
    else:
        return render_template(
            'editItem.html', item=editedItem,
            categories=session.query(Category).all())

    return "page to edit an item"


# create route for deleteItem function here
@app.route('/catalog/<item_title>/delete/', methods=['GET', 'POST'])
def deleteItem(item_title):
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(Item).filter_by(title=item_title).one()
    # alert user just in case the user tries to visit a url
    # that they are not authorized to access
    if itemToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this item. Please create your own item in order to delete.');}</script><body onload='myFunction()'>"  # noqa
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("item deleted!")
        return redirect('/')
    else:
        return render_template('deleteItem.html', item=itemToDelete)


if __name__ == '__main__':
    app.debug = True
    # app.run(host='0.0.0.0', port=8000)
