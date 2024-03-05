import sqlite3

from sqlite3 import Error

# Database Generation


#   Generate Cursor
class database:
    cx = sqlite3.connect("healthdiet.db")
    cursor = cx.cursor()

    # Generate Tables
    
    # Generate table to store individual users
    cursor.execute("CREATE TABLE userlist (id INT, username VARCHAR(255))")
    # Generate table for the contense of the users pantry
    cursor.execute("CREATE TABLE pantry (id INT, username VARCHAR(255), expiry_date DATE, type VARCHAR(255), qunatity INT)")
    # Generate table for food types
    cursor.execute("CREATE TABLE foodtype (id INT, name VARCHAR(255), energyValue int, caloricValue int, fat int, saturatedFat int,carbohydrate int, carboSuger int, fibre int, protein int, salt int)")
    # Generate table for the nutritional intake of the user
    cursor.execute("CREATE TABLE userDietRecord (id INT, name VARCHAR(255), current_date DATE, energyValue int, fat int, saturatedFat int,carbohydrate int, carboSuger int, fibre int, protein int, salt int)")

    cursor.execute("INSERT INTO pantry VALUES (12, 'Hinigaer Beans', 2024/05/12, 'Beans', 5)")

    for row in cursor.execute("SELECT * FROM pantry"):
        print(row)
    # get function for finding user ID based on username
    
    def getuserID(string):
        userID = cursor.execute("SELECT id FROM userlist WHERE username IS "+string)
        return userID
    cx.close()
# Health Tracker
class healthTracker:
    def getany():
        return
# Recipe Planner
class RecipePlanner:
    def getany():
        return
# User Interface
class UnserInterface:
    def getany():
        return
# Health IO
class HealthIO:
    def getany():
        return
# Pantry IO    
class PantryIO:
    def getany():
        return