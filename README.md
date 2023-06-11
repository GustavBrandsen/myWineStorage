# myWineStorage - Keep track of your wine!

# running myWineStorage:
Assumes a working Python 3 installation (with python=python3 and pip=pip3).

(1) Run the code below to install the dependencies.
>$ pip3 install -r requirements.txt

(2) Initialize the database, by running the SQL file (Creating the necessary tables, views, triggers etc.) 
IMPORTANT: In the 'intialize_database.SQL' change the directory to the full path of the 'wine_info.csv' file. 

(3) In the app.py-file, set your own database username and password

(4) Run Web-App
>$ python3 src/app.py


----------------------------------------------------------------------------------------------

# How to use the application:

We have implemented the folowing functionality to myWineStorage:

1 - Create user. You can register as a user by clicking "Register" and filling out the form.

2 - A registered user can login by clicking "Login" and filling out the form.

3 - On the tab "Wines" the user can access a huge database of wine and lookup prices, types and much more. 

4 - The user can create their own wine locations on the page "Locations". This page also display an overview of all the users location with a sum of all wines registered at each location. 

5 - On the home page, the user can register wines from the wine database and place them in the desired location. A wine is registered by inputting the name of the Wine (Has to match exactly, so paste from the Wines page), choose a location and a quantity.


Other notes about implementation:

We have create sequences, functions and triggers for ID's allocation across Users, UserWines and Locations.