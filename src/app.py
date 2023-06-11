from flask import Flask, render_template, redirect, url_for, session, abort, request, flash
import requests
from bs4 import BeautifulSoup
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import psycopg2
import os
import glob
import pandas as pd
import random

app = Flask(__name__)

# set your own database name, username and password
# potentially wrong password
db = "dbname='Wine' user='postgres' host='localhost' password='password'"
conn = psycopg2.connect(db)
connection = conn.cursor()


def queryCommit():
    commit_query = f''' commit; '''
    connection.execute(commit_query)


@app.route('/')
def home():
    home_header = "Home"
    user_name = ""
    headers = []
    tableData = []
    locData = []
    if 'user_id' in session:
        headers = ['Wine', 'Location', 'Quantity']

        user_wines_query = f''' SELECT * FROM user_wines where uw_user_id = {str(session['user_id'])}'''
        connection.execute(user_wines_query)
        fetch_user_wines = connection.fetchall()


        user_wines_query = f''' SELECT * FROM user_wines_v WHERE uw_user_id = {str(session['user_id'])}'''
        connection.execute(user_wines_query)
        fetch_user_wines = connection.fetchall()

        for i in range(len(fetch_user_wines)):
            wine_id = fetch_user_wines[i][1]
            loc_id = fetch_user_wines[i][2]
            wine_quant = fetch_user_wines[i][3]

            tableData.append(
                {'Wine': wine_id, 'Location': loc_id, 'Quantity': wine_quant})
        if len(fetch_user_wines) == 0:
            tableData.append(
                {'Wine': "None", 'Location': "None", 'Quantity': "None"})

        # GET ALL LOCATION NAMES FOR THE SPECIFIC USER
        user_loc_query = f''' SELECT * FROM locations '''
        connection.execute(user_loc_query)
        fetch_user_loc = connection.fetchall()

        for i in range(len(fetch_user_loc)):
            loc_id = fetch_user_loc[i][0]
            loc_name = fetch_user_loc[i][1]
            loc_user_id = fetch_user_loc[i][2]

            if (loc_user_id == session['user_id']):
                locData.append(loc_name)

    if 'username' in session:
        user_name = session['username']
        home_header = "Welcome, " + session['username'] + "!"

    return render_template('home.html', header_value=home_header, headers=headers, tableData=tableData, locData=locData, userName = user_name)


@app.route('/', methods=['POST'])
def add_wine():
    if ("rem_wine_name" in request.form and "rem_loc_name" in request.form and "rem_wine_qty" in request.form):
        rem_wine_name = request.form['rem_wine_name']
        rem_loc_name = request.form['rem_loc_name']
        rem_wine_qty = request.form['rem_wine_qty']

        rem_wine_id = f'''SELECT wine_id FROM Wines where wine_name = '{rem_wine_name}' '''
        connection.execute(rem_wine_id)
        wine_id = connection.fetchone()[0]
        
        rem_loc_id = f'''SELECT loc_id FROM locations where loc_name = '{rem_loc_name}' AND loc_user_id = {session['user_id']}; '''
        connection.execute(rem_loc_id)
        loc_id = connection.fetchone()[0]

        delete_quert = f'''DELETE FROM user_wines WHERE uw_wine_id = {wine_id} AND uw_loc_id = {loc_id} AND uw_qty = {rem_wine_qty};'''
        connection.execute(delete_quert)
        queryCommit()


    if ("add_wine_name" in request.form and "add_wine_loc" in request.form and "add_wine_qty" in request.form):
        add_wine_name = request.form['add_wine_name']
        add_wine_loc = request.form['add_wine_loc']
        add_wine_qty = request.form['add_wine_qty']
        if add_wine_qty == "":
            add_wine_qty = 1
        elif not add_wine_qty.isdigit():
            flash("Quantity must be a positive integer")
            return redirect(url_for("home"))
        elif int(add_wine_qty) < 1:
            flash("Quantity must be a positive integer")
            return redirect(url_for("home"))
        else:
            add_wine_qty = int(add_wine_qty)

        add_wine_id = f'''SELECT wine_id FROM wines WHERE wine_name = '{add_wine_name}' '''
        connection.execute(add_wine_id)
        wine_ids = connection.fetchall()
        if len(wine_ids) == 0:
            flash("Wine doesn't exists")   
        else: 
            if add_wine_loc == "":
                flash("Choose a location for your wine!")
            else:
                add_loc_id = f'''SELECT loc_id FROM locations WHERE loc_name = '{add_wine_loc}' AND loc_user_id = {session['user_id']};'''
                connection.execute(add_loc_id)
                loc_id = connection.fetchone()
                if loc_id == None:
                    flash("Choose a location!")
                else:
                    query = f'''INSERT INTO user_wines 
                    (uw_user_id, uw_wine_id, uw_loc_id, uw_qty) 
                    VALUES ({session['user_id']}, {wine_ids[0][0]}, {loc_id[0]}, {add_wine_qty});'''
                    connection.execute(query)
                    queryCommit()
    return redirect(url_for("home"))
    
@app.route('/locations', methods=['POST'])
def add_location():
    if ("add_loc_name" in request.form):
        add_loc_name = request.form['add_loc_name']

        get_all_loc_names = f''' SELECT loc_name FROM locations where loc_user_id = {session['user_id']} '''
        connection.execute(get_all_loc_names)
        locations = connection.fetchall()
        loc_names = []
        for i in range(len(locations)):
            loc_names.append(locations[i][0].strip())

        if add_loc_name in loc_names:
            flash("Location name already exists!")
        elif add_loc_name == "":
            flash("Enter a location name!")
        else:
            insert_quert = f'''INSERT INTO locations (loc_name, loc_user_id) VALUES ('{add_loc_name}', {session['user_id']});'''
            connection.execute(insert_quert)
            queryCommit()
        
    if ("rem_loc_name" in request.form):
        rem_loc_name = request.form['rem_loc_name']
        rem_loc_amount = request.form['rem_loc_amount']
        
        if rem_loc_amount == "None":
            delete_quert = f'''DELETE FROM locations WHERE loc_name = '{rem_loc_name}' AND loc_user_id = {session['user_id']};'''
            connection.execute(delete_quert)
            queryCommit()
        else:
            flash("You can't delete locations with wines!")
    return redirect(url_for("locations"))

@app.route('/locations')
def locations():
    header = []
    locData = []
    if 'user_id' in session:
        header = ['Location', 'Amount of Wines']

        user_loc_query = f''' SELECT * FROM user_wines_sum WHERE loc_user_id = {session['user_id']}'''
        connection.execute(user_loc_query)
        fetch_user_loc = connection.fetchall()

        for i in range(len(fetch_user_loc)):
            loc_user_id = fetch_user_loc[i][0]
            loc_name = fetch_user_loc[i][1]
            loc_amount = fetch_user_loc[i][2]
            
            locData.append({'name': loc_name, 'amount': loc_amount})

    return render_template('locations.html', header=header, locData=locData)

@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']

    query = f''' SELECT * FROM users WHERE user_name = '{username}' and user_password = '{password}' '''

    connection.execute(query)

    fetchall = connection.fetchall()

    if (len(fetchall) != 0):
        fetch_user_id = fetchall[0][0]
        fetch_user_name = fetchall[0][1]
        fetch_user_pass = fetchall[0][2]

        
        session['logged_in'] = True
        session['username'] = username
        session['user_id'] = fetch_user_id
        return redirect(url_for("home"))
    else:
        flash('Wrong password or username!')
        return redirect(url_for("login"))


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def do_register():
    username = request.form['username']
    password = request.form['password']

    query2 = f''' SELECT * FROM users where user_name = '{username}' '''

    connection.execute(query2)

    if (len(connection.fetchall()) != 0):
        flash('Username taken!')
        return redirect(url_for("register"))
    else:
        query3 = f''' INSERT INTO users(user_name, user_password) VALUES('{username}', '{password}'); '''
        connection.execute(query3)
        queryCommit()
        return redirect(url_for("home"))


@app.route('/wines')
def wines():
    headers = []
    tableData = []
    wines_query = f''' SELECT * FROM wines '''
    connection.execute(wines_query)
    fetch_wines = connection.fetchall()

    headers = ["Name", "Producer", "Nation", "Local", "Varieties",
               "Type", "Abv", "Degree", "Price", "Year", "ml"]

    for i in range(len(fetch_wines)):
        wine_name = fetch_wines[i][1]
        wine_producer = fetch_wines[i][2]
        wine_nation = fetch_wines[i][3]
        wine_local = fetch_wines[i][4]
        wine_varieties = fetch_wines[i][5]
        wine_type = fetch_wines[i][6]
        wine_abv = fetch_wines[i][7]
        wine_degree = fetch_wines[i][8]
        wine_price = fetch_wines[i][9]
        wine_year = fetch_wines[i][10]
        wine_ml = fetch_wines[i][11]

        tableData.append(
            {'Name': wine_name, 'Producer': wine_producer, 'Nation': wine_nation, 'Local': wine_local, 'Varieties': wine_varieties, 'Type': wine_type, 'Abv': wine_abv, 'Degree': wine_degree, 'Price': wine_price, 'Year': wine_year, 'ml': wine_ml})

    return render_template('wines.html', headers=headers, tableData=tableData)



@app.route('/logout')
def logout():
    session.clear()

    return render_template('logout.html')

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)
