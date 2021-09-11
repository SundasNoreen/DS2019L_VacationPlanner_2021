
## Welcome to Vacation Planner!

## Installation Guide

The Project requires any Python IDE to run. Pycharm will be preferred here.

- Download the project as Zip File.
- Extract it.
- Open the IDE, open the project's location.
- Set a Valid Python Interpreter.
- Run the requirements.txt file to install the modules.
```sh
pip install -r requirements.txt
```

For Database Connection...

- In order to connect Database, you can either use cloud or local host. Simply, import 'trips.sql' in your mysql server.
- Edit the following part of code according to your database.
```sh
db = pymysql.connect(host='', user='', password='', database='trips')
```

Run the Code, it will run on your machine.
 

## Configuration Guide
 Following Points can be accessed from Home Page: 
- **Holiday Destinations:**
The Best places to visit in Pakistan's top ten travel destinations.
- **Hotels:**
Get Hotel Information (name + price) for around 18 of Pakistan's cities.
- **Scheduled Trips:**
Get Details of scheduled trips, both current and future.
- **Trips History:**
It displays trips that have been completed, that is, those whose end date has passed.
- **Travel Costs:**
Allows you to compute the average cost of two cities, and it works over 150 Pakistani cities.
- **Plan Trips:**
It allows you to search for hotels within your ideal budget, plan a vacation to your desired location (the Vacation Planner will calculate both travel and hotel costs), and plan a vacation within your budget constraints (The Vacation Planner will show all the places that can be travelled to within that budget, the user can then select any trip of his choice). Click on the **Save Trip** Button, your trip will get saved and you will also receive an **email**.
 <br><br>  





