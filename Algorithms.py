# Algorithms for Travel Planner

import pandas as pd
import math
import pymysql
from datetime import datetime


# Helper Functions

def Set_price(j):
    k = (j[3:])
    l = k.replace(',', '')
    m = int(l)
    return m

def FindResidence(budget):
    locations=[]
    price=[]
    results=[]
    amount=[]
    db = pymysql.connect(host='vacation-planner.mysql.database.azure.com', user='sundasnoreen@vacation-planner',
                         password='Sundas1234', database='trips')
    cursor=db.cursor()
    sql = "SELECT `location` FROM `Hotels`;"
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        locations.append(row[0])
    mylist = list(dict.fromkeys(locations))
    for i in mylist:
        sql = "SELECT `price` FROM `Hotels` WHERE `location`=%s;"
        cursor.execute(sql,(i))
        rows = cursor.fetchall()
        for k in rows:
            j = k[0]
            price.append(j)
        sum = 0
        for k in price:
            value = Set_price(k)
            sum = sum + value
        Price = sum / (len(price))
        Price=int(Price)
        if Price <= budget:
            print(Price)
            results.append(i)
            amount.append(Price)
    info=zip(results,amount)
    db.close()
    return info


# Class Algoithms

class Algorithms:


   # Calculate Distance and Cost Between Two Places.

    def Distance_and_Cost(Starting,Destination):
        Start = []
        End = []
        db = pymysql.connect(host='vacation-planner.mysql.database.azure.com', user='sundasnoreen@vacation-planner',
                             password='Sundas1234', database='trips')
        cursor = db.cursor()
        sql = "SELECT * FROM `pk` WHERE `city`=%s;"
        cursor.execute(sql,Starting)
        rows = cursor.fetchall()
        for row in rows:
            Start.append(row[1])
            Start.append(row[2])
        sql1 = "SELECT * FROM `pk` WHERE `city`=%s;"
        cursor.execute(sql1, Destination)
        row = cursor.fetchall()
        for i in row:
            End.append(i[1])
            End.append(i[2])
        lat1 = math.radians(Start[0])
        lon1 = math.radians(Start[1])
        lat2 = math.radians(End[0])
        lon2 = math.radians(End[1])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        R = 6373.0
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        by_road = distance + 50
        cost_per_person = 3 * by_road
        db.close()
        return [cost_per_person,by_road,distance]


    # Calculate Number of Days between two dates.

    def Number_of_Days(d0,d1):
        d0 = datetime.strptime(d0, "%Y-%m-%d")
        d1 = datetime.strptime(d1, "%Y-%m-%d")
        delta = d0 - d1
        days = delta.days
        return days


    # Knowing the Destinaion, Plan the Trip.

    def FindDestination (Destination,Starting,People,checkin,checkout):
        no=Algorithms.Number_of_Days(checkout,checkin)
        values=Algorithms.Distance_and_Cost(Starting,Destination)
        cost=values[0]
        people=int(People)
        overall_cost = cost*people*2
        if people==1:
            hotel_rooms=1
        elif people%2==0:
            hotel_rooms = people / 2
        else:
            hotel_rooms = (people-1) / 2
        price=[]
        db = pymysql.connect(host='vacation-planner.mysql.database.azure.com', user='sundasnoreen@vacation-planner',
                             password='Sundas1234', database='trips')
        cursor = db.cursor()
        sql = "SELECT `price` FROM `Hotels` WHERE `location`=%s;"
        cursor.execute(sql, Destination)
        rows = cursor.fetchall()
        try:
            for i in rows:
                j=i[0]
                price.append(j)
            if (price==[]):
                residence="Cannot be Determined."
                return [int(overall_cost), residence, overall_cost]
            else:
                sum = 0
                for k in price:
                    value=Set_price(k)
                    sum=sum+value
                print(len(price))
                Price=sum/(len(price))
                residence=hotel_rooms*Price*no
                residence=residence-(residence*0.14)
                final_cost=residence+overall_cost
                Final_Cost=int(final_cost)
                return [int(overall_cost),int(residence),int(Final_Cost),int(no)]
        except Exception as e:
            print(e)
        finally:
            db.close()

    # Find Hotels within Budget.

    def FindHotelinBudget(Minimum,Maximum,Location):
        db = pymysql.connect(host='vacation-planner.mysql.database.azure.com', user='sundasnoreen@vacation-planner',
                             password='Sundas1234', database='trips')
        cursor = db.cursor()
        picture=[]
        name=[]
        Price=[]
        location=[]
        info=""
        Minimum=int(Minimum)
        Maximum=int(Maximum)
        sql = "SELECT * FROM `Hotels` WHERE `location`=%s;"
        cursor.execute(sql, Location + " ")
        rows = cursor.fetchall()
        for row in rows:
            price=Set_price(row[4])
            if price<=Maximum and price>=Minimum:
                picture.append(row[2])
                name.append(row[1])
                Price.append(row[4])
                location.append(Location)
                info = zip(picture, name, location, Price)
        db.close()
        return info


    # Find Hotels Below Budget.

    def FindHotelbelow(Minimum,Maximum,Location):
        db = pymysql.connect(host='vacation-planner.mysql.database.azure.com', user='sundasnoreen@vacation-planner',
                             password='Sundas1234', database='trips')
        cursor = db.cursor()
        picture=[]
        name=[]
        Price=[]
        location=[]
        info=""
        Minimum=int(Minimum)
        Maximum=int(Maximum)
        sql = "SELECT * FROM `Hotels` WHERE `location`=%s;"
        cursor.execute(sql, Location + " ")
        rows = cursor.fetchall()
        for row in rows:
            price=Set_price(row[4])
            if price<=Maximum:
                picture.append(row[2])
                name.append(row[1])
                Price.append(row[4])
                location.append(Location)
                info = zip(picture, name, location, Price)
        db.close()
        return info


    # Knowing the Budget, Find the Trip.

    def FindBudget (Budget,Starting,People,checkin,checkout):
        destination=[]
        travel_costs=[]
        residence_costs=[]
        final=""
        no = Algorithms.Number_of_Days(checkout, checkin)
        Budget=int(Budget)
        if Budget<=15000:
            Budget=Budget+2000
        elif Budget>15000:
            Budget=Budget
        people=int(People)
        travel=int(Budget/2)
        distance = travel/(people*2*3)
        residence=int(Budget/2)
        residence_msg=""
        if people==1:
            rooms=1
        elif people%2==0:
            rooms = people / 2
        else:
            rooms = (people-1) / 2
        residence = residence/(no*rooms)
        residence=int(residence)
        overall=[]
        info=FindResidence(residence)
        result_set=set(info)
        print(result_set)
        for row in result_set:
            if row[0]!=Starting:
                travel = Algorithms.Distance_and_Cost(Starting, row[0])
                by_road = travel[1]
                if row[1]=="":
                    residence_msg="Residence can't be afforded in the Given Budget."
                    destination.append(row[0])
                    m=Budget/(3 * 2 * people)
                    travel_costs.append(int(m))
                    residence_costs.append(residence_msg)
                    overall.append(m)
                elif by_road<(Budget/(people*2*3)):
                    destination.append(row[0])
                    m = by_road * 3 * 2 * people
                    travel_costs.append(int(m))
                    n=row[1]*no*rooms
                    residence_costs.append(int(n))
                    overall.append(int(m+n))
        length=len(destination)
        final=zip(destination,travel_costs,residence_costs,overall)
        # lists=Algorithms.Bubble_Sort(list(final))
        res = sorted(final, key=lambda x: x[3])
        return [res,no,length]

    def Bubble_Sort(list_):
        ith = 1
        list_length = len(list_)
        for i in range(0, list_length):
            for j in range(0, list_length-i-1):
                if (list_[j][ith] > list_[j + 1][ith]):
                    temp = list_[j]
                    list_[j]= list_[j + 1]
                    list_[j + 1]= temp


    def binarySearch(arr, x):
        mid=int(len(arr)/2)
        l=arr[mid]
        for index, tuple in enumerate(arr):
            if (index==mid):
                id = tuple[0]
                if id == x:
                    l=(l,)
                    return l
                elif id < x:
                    return Algorithms.binarySearch(arr[mid:],x)
                else:
                    return Algorithms.binarySearch(arr[:mid],x)










