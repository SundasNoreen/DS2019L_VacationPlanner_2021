# Travel Planner

# Importing Neccessary Libraries and Modules

from flask import Flask, request, render_template, redirect, url_for, session
from functools import wraps
import random , gc , math , pymysql , smtplib , ssl
import pandas as pd
from datetime import timedelta, date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dateutil.relativedelta import relativedelta
import Algorithms

# Function for Database Connection


def database():
    db = pymysql.connect(host='', user='',
                         password='', database='trips')
    return db


# Defining App

app = Flask(__name__)
app.secret_key = 'sundas'


# Session Time-Out

@app.before_request
def Session_Timeout():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=31)


# First Display Page.

@app.route('/')
def Index():
    if 'logged in':
        return redirect(url_for('Home_Page'))
    return redirect(url_for('login'))


# Error Page

@app.route('/error')
def page_not_found():
    return render_template('Error.html')


# Login Function.

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    conn=database()
    cursor=conn.cursor()
    if request.method == 'POST':
        Email = request.form['email']
        Password = request.form['password']
        try:
            sql = 'SELECT * FROM `userdata`'
            cursor.execute(sql)
            read = cursor.fetchall()
            for row in read:
                if Email != row[0] or Password != row[2]:
                    error = 'Invalid Credentials. Please try again.'
                else:
                    session['logged in'] = True
                    session['email'] = row[0]
                    session['name'] = row[1]
                    session['password'] = row[2]
                    return redirect(url_for('Home_Page'))
        except:
            error = "Sorry, We couldn't Log you In, Please Try Again."
        finally:
            conn.close()
    return render_template('login.html', error=error)


# Signup Function.

@app.route('/sign_up', methods=['GET', 'POST'])
def Signup_Page():
    error = ''
    flag = ''
    conn = database()
    cursor = conn.cursor()
    try:
        if request.method == 'POST':
            Name = request.form['name']
            Email = request.form['email']
            Password = request.form['password']
            repeat = request.form['repeat']
            sql = 'SELECT `email` FROM `userdata`'
            cursor.execute(sql)
            read = cursor.fetchall()
            for i in read:
                j = i[0]
                if j == Email:
                    flag = 'false'
                    error = 'Email Already Exists. Login Your Account.'
            if flag != 'false':
                if repeat != Password:
                    error = "Passwords doesn't match."
                else:
                    sql = 'INSERT into `userdata`(`email`, `name`, `password`) VALUES (%s,%s,%s)'
                    cursor.execute(sql, (Email, Name, Password))
                    conn.commit()
                    return redirect(url_for('login'))
    except:
        error = "Sorry, We couldn't Register You, Please Try Again."
    finally:
        conn.close()
    return render_template('signup.html', error=error)


# Session for User.

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return decorated_function


# Logout to Clear all Existing Sessions.

@app.route('/logout')
@login_required
def logout():
    session.clear()
    gc.collect()
    return redirect(url_for('login'))


# Display User Profile

@app.route('/profile')
@login_required
def Profile():
    return render_template('profile.html', name=session['name'], email=session['email'])

@app.route('/about_us')
@login_required
def About():
    return render_template('about.html', name=session['name'], email=session['email'])

@app.route('/services')
@login_required
def Services():
    return render_template('services.html', name=session['name'], email=session['email'])

@app.route('/acknowledgements')
@login_required
def Acknowledgements():
    return render_template('Ack.html', name=session['name'], email=session['email'])

# Delete Account Permanently.

@app.route('/close_account', methods=['GET', 'POST'])
@login_required
def Close_Account():
    error = "You are Closing Your Account, this action can't be undone."
    Password = session['password']
    username = session['email']
    conn = database()
    cursor = conn.cursor()
    try:
        if request.method == 'POST':
            password = request.form['password']
            if Password != password:
                error = 'Passwords is not correct.'
            elif password == Password:
                sql = 'DELETE FROM `userdata` WHERE `email`=%s'
                sql1 = 'DELETE FROM `past_trips` WHERE `email`=%s'
                cursor.execute(sql, username)
                cursor.execute(sql1, username)
                conn.commit()
                return redirect(url_for('logout'))
    except:
        error = "There seems to be some error, Please Try Again."
    finally:
        conn.close()
    return render_template('close.html', error=error, user=session['name'], name=session['name'],email=session['email'])


# Change Password

@app.route('/password', methods=['GET', 'POST'])
@login_required
def Password():
    error = ''
    username = session['email']
    Password = session['password']
    conn = database()
    cursor = conn.cursor()
    try:
        if request.method == 'POST':
            Pre = request.form['pre']
            New = request.form['new']
            repeat = request.form['repeat']
            if repeat != New:
                error = "Passwords doesn't match."
            elif Pre != Password:
                error = 'Please Enter Your Correct Current Password.'
            elif Pre == New:
                error = 'You are using your Current Password.'
            elif repeat == New and Pre == Password:
                sql = 'UPDATE `userdata` SET `password`=%s WHERE `email`=%s'
                cursor.execute(sql, (New, username))
                conn.commit()
                return redirect(url_for('logout'))
            else:
                error = "Password couldn't be changed.Please Try Again Later."
    except:
        error = "There Seems to be some Problem, Please Try Again."
    finally:
        conn.close()
    return render_template('password.html', error=error, name=session['name'])


# Forget Password by Sending an OTP usig EMail

@app.route('/forget_password', methods=['GET', 'POST'])
def Send_Mail():
    error = ''
    conn = database()
    cursor = conn.cursor()
    try:
        if request.method == 'POST':
            session['em'] = request.form['email']
            sql = 'SELECT `email` FROM `userdata`'
            cursor.execute(sql)
            read = cursor.fetchall()
            for i in read:
                j = i[0]
                if j == session['em']:
                    sender_email = 'noreply.vacationplanner@gmail.com'
                    password = ''
                    message = MIMEMultipart('alternative')
                    message['Subject'] = \
                        'Vacation Planner Account Password Reset'
                    message['From'] = sender_email
                    message['To'] = j
                    c = ''
                    digits = [i for i in range(0, 10)]
                    for i in range(6):
                        index = math.floor(random.random() * 10)
                        c += str(digits[index])
                    html = \
                        """\
                            <html>
                              <body>
                              <center><h2 style="color:darkcyan">Vacation Planner Account Password Reset</h2></center>
                                <p>Please use this OTP to reset the password for the Vacation Planner Account.<br><br>
                                Here is your OTP: """ \
                        + c \
                        + """<br><br>
                                Thanks,<br>
                                The Vacation Planner Team</p>
                                <h4 style="color:darkcyan">Note: This is an auto generated message. Please don't reply to it.
                                </h6>
                              </body>
                            </html>
                            """
                    part = MIMEText(html, 'html')
                    message.attach(part)
                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465,
                            context=context) as server:
                        server.login(sender_email, password)
                        server.sendmail(sender_email, j,
                                message.as_string())
                    session['code'] = c
                    return redirect(url_for('Get_OTP'))
                else:
                    error = 'There is no such Email in our Database.'
    except:
        error = 'There was an error in sending OTP. Please, Try Again.'
    finally:
        conn.close()
    return render_template('forget.html', error=error)


# Enter OTP Page.

@app.route('/enter_OTP', methods=['GET', 'POST'])
def Get_OTP():
    error = ''
    OTP = session['code']
    try:
        if request.method == 'POST':
            code1 = request.form['OTP']
            if OTP == code1:
                session['code'] = ''
                return redirect(url_for('Password_Reset'))
            else:
                error = 'Invalid OTP.'
    except:
        return redirect(url_for('page_not_found'))
    return render_template('Enter_Code.html', error=error, user=session['em'])


# Reset Password Page

@app.route('/reset_password', methods=['GET', 'POST'])
def Password_Reset():
    error = ''
    username = session['em']
    conn = database()
    cursor = conn.cursor()
    try:
        if request.method == 'POST':
            New = request.form['new']
            repeat = request.form['repeat']
            if repeat == New:
                sql = 'UPDATE `userdata` SET `password`=%s WHERE `email`=%s'
                cursor.execute(sql, (New, username))
                conn.commit()
                return redirect(url_for('logout'))
            else:
                error = 'Passwords doesnot match.'
    except:
        error = "Passwords couldn't be updated."
    finally:
        conn.close()
    return render_template('reset.html', error=error, user=session['em'])


# Display HomePage with Menus.

@app.route('/home_page')
@login_required
def Home_Page():
    return render_template('home.html', name=session['name'])


# Display Trips History

@app.route('/trips_history')
@login_required
def Trips_History():
    rows = ''
    error=''
    today = date.today()
    d1 = today.strftime('%y-%m-%d')
    conn = database()
    cursor = conn.cursor()
    sql = 'SELECT * FROM `past_trips` WHERE `email`=%s AND `Ending_Date`<%s ORDER BY Ending_Date DESC; '
    try:
        cursor.execute(sql, (session['email'], d1))
        rows = cursor.fetchall()
    except:
        error=" Unable to fetch data."
    finally:
        conn.close()
    return render_template('trips_history.html', name=session['name'],rows=rows)


# Display Trips Schedule

@app.route('/scheduled_trips')
@login_required
def Scheduled_Trips():
    rows = ''
    entries = ''
    today = date.today()
    d1 = today.strftime('%y-%m-%d')
    conn = database()
    cursor = conn.cursor()
    try:
        sql =  'SELECT * FROM `past_trips` WHERE `email`=%s AND `Ending_Date`>=%s AND `Starting_Date`<=%s ORDER BY Starting_Date DESC; '
        sql1 = 'SELECT * FROM `past_trips` WHERE `email`=%s AND `Starting_Date`>%s ORDER BY Starting_Date; '
        cursor.execute(sql, (session['email'], d1, d1))
        rows = cursor.fetchall()
        cursor.execute(sql1, (session['email'], d1))
        entries = cursor.fetchall()
    except:
        return redirect(url_for('page_not_found'))
    finally:
        conn.close()
    return render_template('scheduled_trips.html', name=session['name'], rows=rows, entries=entries)


# Display Details of a Particular Trip.

@app.route('/trip_<beta>')
@login_required
def My_Trip(beta):
    rows = ''
    conn = database()
    cursor = conn.cursor()
    try:
        sql = 'SELECT * FROM `past_trips`'
        cursor.execute(sql)
        row = cursor.fetchall()
        work=Algorithms
        rows=list(work.Algorithms.binarySearch(row,int(beta)))
    except:
        return redirect(url_for('page_not_found'))
    finally:
        conn.close()
    return render_template('my_trip.html', name=session['name'],rows=rows)


# Explore Page showing Different Cities of Holiday Destinations.

@app.route('/explore')
@login_required
def Explore_Page():
    return render_template('explore.html', name=session['name'])


# Explore Page showing Different Cities for Hotels.

@app.route('/hotels')
@login_required
def Hotels_page():
    return render_template('Hotels_Home.html', name=session['name'])


# View Hotels by City.

@app.route('/hotels_<city>')
@login_required
def Hotels_Details(city):
    error = ''
    info = ''
    picture = []
    name = []
    location = []
    price = []
    conn = database()
    cursor = conn.cursor()
    try:
        sql = 'SELECT * FROM `Hotels` WHERE `location`=%s'
        cursor.execute(sql, city)
        rows = cursor.fetchall()
        for row in rows:
            picture.append(row[2])
            name.append(row[1])
            price.append(row[4])
            location.append(row[0])
        info = zip(picture, name, location, price)
    except:
        error = 'There is some error in fetching data.'
    finally:
        conn.close()
    return render_template('Hotels.html', name=session['name'],
                           info=info, error=error)


# Page Showing Travel Sights / Hotels.

@app.route('/<area>')
@login_required
def Areas(area):
    filename = area + '.csv'
    error = ''
    info = ''
    try:
        data = pd.read_csv(filename)
        data.fillna('', inplace=True)
        ci = []
        picture = []
        details = []
        city = data.city
        for i in city:
            ci.append(i)
            picture.append(data.iloc[data[data['city']
                           == i].index.values[0]]['picture'])
            details.append(data.iloc[data[data['city']
                           == i].index.values[0]]['details'])
        info = zip(ci, picture, details)
        if ci == []:
            error = 'No Sights in our Database.'
    except:
        error = 'There was error in fetching data.'
    return render_template('alphabets.html', name=session['name'],
                           info=info, error=error)


# Select Options via to plan trip.

@app.route('/plan_trip_home_page')
@login_required
def Plan_Home_Page():
    return render_template('PlanTrip.html', name=session['name'])


# Looking For Hotels.

@app.route('/looking_for_hotels', methods=['GET', 'POST'])
@login_required
def Looking_For_Hotels():
    maximum = ''
    minimum = ''
    if request.method == 'POST':
        Location = request.form['location']
        Budget = request.form['amount']
        Budget = int(Budget)
        if Budget == 1:
            minimum = 1000
            maximum = 1500
        elif Budget == 2:
            minimum = 1500
            maximum = 2000
        elif Budget == 3:
            minimum = 2000
            maximum = 2500
        elif Budget == 4:
            minimum = 2500
            maximum = 3000
        elif Budget == 5:
            minimum = 3000
            maximum = 3500
        elif Budget == 6:
            minimum = 3500
            maximum = 4000
        elif Budget == 7:
            minimum = 4000
            maximum = 4500
        elif Budget == 8:
            minimum = 4500
            maximum = 5500
        elif Budget == 9:
            minimum = 5500
            maximum = 6500
        elif Budget == 10:
            minimum = 6500
            maximum = 7500
        elif Budget == 11:
            minimum = 7500
            maximum = float('inf')
        Obj = Algorithms
        info = Obj.Algorithms.FindHotelinBudget(minimum, maximum,
                Location)
        travel = Obj.Algorithms.FindHotelbelow(minimum, maximum,
                Location)
        return render_template('Hotels.html',name=session['name'], info=info, travel=travel)
    return render_template('LookingHotels.html', name=session['name'])


# Plan Trip by Knowing your Destination.

@app.route('/plan_by_destination', methods=['GET', 'POST'])
@login_required
def By_Destination():
    error = ''
    d1 = date.today()
    three_mon_rel = relativedelta(months=3)
    six_mon_rel = relativedelta(months=6)
    d2 = d1 + three_mon_rel
    d3 = d1 + six_mon_rel
    if request.method == 'POST':
        Destination = request.form['location']
        Starting = request.form['starting']
        People = request.form['number']
        CheckIn = request.form['checkin']
        CheckOut = request.form['checkout']
        if People == '5':
            People = '6'
        elif People == '6':
            People = '9'
        elif People == '7':
            People = '12'
        if Destination == Starting:
            error = \
                'Starting Location and Destination cannot be the same.'
        elif CheckOut < CheckIn:
            error = \
                'Check Out Date should not come before Check In Date.'
        else:
            Obj = Algorithms
            travel = Obj.Algorithms.FindDestination(Destination,
                    Starting, People, CheckIn, CheckOut)
            return redirect(url_for(
                'Save_Trip',
                a=Destination,
                b=Starting,
                c=CheckIn,
                d=CheckOut,
                e=People,
                f=travel[0],
                g=travel[1],
                h=travel[2]
                ))

    return render_template('By_Location.html',name=session['name'],d1=d1,d2=d2,d3=d3,error=error, )


# Create Your Own Trip
@app.route('/create_my_trip', methods=['GET', 'POST'])
@login_required
def Create_Own_Trip():
    error = ''
    d1 = date.today()
    three_mon_rel = relativedelta(months=3)
    six_mon_rel = relativedelta(months=6)
    d2 = d1 + three_mon_rel
    d3 = d1 + six_mon_rel

    if request.method == 'POST':
        Travel = request.form['budget']
        Residence = request.form['residence']
        Destination = request.form['location']
        Starting = request.form['starting']
        People = request.form['number']
        CheckIn = request.form['checkin']
        CheckOut = request.form['checkout']
        Obj = Algorithms
        overall = int(Travel) + int(Residence)
        if CheckIn > CheckOut:
            error = \
                'Check Out Date should not come before Check In Date.'
        else:
            return redirect(url_for(
                'Save_Trip',
                a=Destination,
                b=Starting,
                c=CheckIn,
                d=CheckOut,
                e=People,
                f=Travel,
                g=Residence,
                h=int(overall),
                ))
    return render_template(
        'Search.html',
        error=error,
        name=session['name'],
        d1=d1,
        d2=d2,
        d3=d3,
        )


# Save your Trip.

@app.route('/save_<a>_<b>_<c>_<d>_<e>_<f>_<g>_<h>', methods=['GET', 'POST'])
@login_required
def Save_Trip(a,b,c,d,e,f,g,h):
    conn = database()
    cursor = conn.cursor()
    error = \
        'The Costs are an average calculation by the system.'
    if request.method == 'POST':
        try:
            sql = \
                'INSERT into `past_trips`(`Location`, `Destination`, `Starting_Date`, `Ending_Date`, `email`, `travel`,`hotel`, `overall`, `people`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            cursor.execute(sql, (
                b,
                a,
                c,
                d,
                session['email'],
                f,
                g,
                h,
                e,
                ))
            conn.commit()
            sender_email = 'noreply.vacationplanner@gmail.com'
            receiver_email = session['email']
            password = ''
            message = MIMEMultipart('alternative')
            message['Subject'] = 'Trip Saved'
            message['From'] = sender_email
            message['To'] = receiver_email

            html = \
                """\
                                            <html>
                                              <body>
                                              <center><h2 style="color:darkcyan"> Trip Saved</h2></center>
                                                <p>
                                                Dear """ \
                + session['name'] \
                + """,<br><br>
                                                Your Trip with the Following Details is being by saved by Vacation Planner.<br><br>
                                                <strong>Starting Location: </strong>""" \
                + b \
                + """<br>
                                                <strong>Destination: </strong>""" \
                + a \
                + """<br>
                                                <strong>Number of People: </strong>""" \
                + e \
                + """<br>
                                                <strong>Check In Date: </strong>""" \
                + c \
                + """<br>
                                                <strong>Check Out Date: </strong>""" \
                + d \
                + """<br>
                                                <strong>Travel Cost: </strong>""" \
                + f \
                + """<br>
                                                <strong>Residence Cost: </strong>""" \
                + g \
                + """<br>
                                                <strong>Overall Cost: </strong>""" \
                + h \
                + """<br>
                                                <br>
                                                Thanks,<br>
                                                The Vacation Planner Team</p>
                                                <h4 style="color:darkcyan">Note: This is an auto generated message. Please don't reply to it.
                                                </h6>
                                              </body>
                                            </html>
                                            """
            part2 = MIMEText(html, 'html')
            message.attach(part2)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465,
                                  context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email,
                                message.as_string())
            session['code'] = c
            error = 'Trip Successfully Saved.'
        except:
            error="There seems to be some Problem , Please Try Again."
        finally:
            conn.close()
    return render_template(
        'Save.html',
        name=session['name'],
        error=error,
        a=a,
        b=b,
        c=c,
        d=d,
        e=e,
        f=f,
        g=g,
        h=h,
        )


# Calculate the Travel Cost.

@app.route('/travel_costs', methods=['GET', 'POST'])
@login_required
def Travel_Costs():
    error = ''
    if request.method == 'POST':
        Destination = request.form['to']
        Starting = request.form['from']
        if Destination == Starting:
            error = \
                'Starting Location and Destination cannot be the same.'
        else:
            Obj = Algorithms
            [cost, distance, air] = \
                Obj.Algorithms.Distance_and_Cost(Starting, Destination)
            one = int(cost) * 2
            return render_template(
                'Results.html',name=session['name'],
                a=Destination,
                b=Starting,
                one=int(one),
                c=int(cost),
                d=int(distance),
                e=int(air)
                )
    return render_template('Travel_Costs.html', name=session['name'],
                           error=error)

# Plan Trip by Knowing your Budget.

@app.route('/plan_by_budget', methods=['GET', 'POST'])
@login_required
def By_Budget():
    error = ''
    d1 = date.today()
    three_mon_rel = relativedelta(months=3)
    six_mon_rel = relativedelta(months=6)
    d2 = d1 + three_mon_rel
    d3 = d1 + six_mon_rel
    if request.method == 'POST':
        Budget = request.form['budget']
        Starting = request.form['location']
        People = request.form['number']
        CheckIn = request.form['checkin']
        CheckOut = request.form['checkout']
        m = 0
        if Budget == '1':
            m = 5000
        elif Budget == '2':
            m = 10000
        elif Budget == '3':
            m = 15000
        elif Budget == '4':
            m = 20000
        elif Budget == '5':
            m = 30000
        elif Budget == '6':
            m = 40000
        elif Budget == '7':
            m = 50000
        elif Budget == '8':
            m = 2000000
        if m < 500:
            error = \
                'Your Budget is quite low, we are afraid we might not be able to find trip for you.'
        else:
            Obj = Algorithms
            final = Obj.Algorithms.FindBudget(m, Starting, People,
                    CheckIn, CheckOut)
            no = final[1]
            trip = final[2]
            others = final[0]
            if CheckIn > CheckOut:
                error = 'Check Out Date should not come before Check In Date.'
            else:
                return render_template('Proceed.html',name=session['name'],others=others,trip=trip,starting=Starting,checkin=CheckIn,checkout=CheckOut,people=People)
    return render_template('By_Budget.html',name=session['name'], error=error, d1=d1, d2=d2,
                           d3=d3)

@app.route('/<i>_<j>_<k>_<l>_<m>_<n>_<o>_<p>', methods=['GET', 'POST'])
@login_required
def Proceed_Trip(i,j,k,l,m,n,o,p):
    conn = database()
    cursor = conn.cursor()
    error ='The Costs are an average calculation by the system.'
    if request.method == 'POST':
        try:
            sql = 'INSERT into `past_trips`(`Location`, `Destination`, `Starting_Date`, `Ending_Date`, `email`, `travel`,`hotel`, `overall`, `people`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            cursor.execute(sql, (i,j,k,l,session['email'],m,n,o,p))
            conn.commit()
        except error as e:
            print(e)
        finally:
            conn.close()
    return render_template('Save.html',name=session['name'],a=i,b=j,c=k,d=l,e=m,f=n,g=p,h=o)

if __name__ == '__main__':
    app.run(debug=True)
