from asyncio.windows_events import NULL
from cgitb import grey
from genericpath import exists
from site import addusersitepackages
import sqlite3

from sqlite3 import Cursor, Error
from tarfile import NUL
import tkinter

from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
from turtle import width
from typing import Any

# class to create and manage database
class programDatabase:
    # constructor
    def __init__(self, username):
        self.username = username
        # create foodtype table
        sqlFoodtypeString = """
        CREATE TABLE IF NOT EXISTS foodtype(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE, 
            caloricValue INTEGER,
            energyValue INTEGER,
            fatValue INTEGER,
            fatSaturatedValue INTEGER,
            carbohydrateValue INTEGER,
            carboSugarValue INTEGER,
            fibre INTEGER,
            protein INTEGER,
            salt INTEGER
        );
        """
        self.executeQuery(sqlFoodtypeString)
        # create pantry table
        sqlPantryString = """
        CREATE TABLE IF NOT EXISTS pantry(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            foodtypeID INTEGER,
            expiryDate DATE,
            quantity INTEGER,
            FOREIGN KEY (foodtypeID) REFERENCES foodtype (id) 
        );
        """
        self.executeQuery(sqlPantryString)
        # create personal diet table
        sqlPersonalDiet = """
        CREATE TABLE IF NOT EXISTS diet(
            username TEXT NOT NULL UNIQUE,
            date DATE,
            caloricValue INTEGER,
            energyValue INTEGER,
            fatValue INTEGER,
            fatSaturatedValue INTEGER,
            carbohydrateValue INTEGER,
            carboSugarValue INTEGER,
            fibre INTEGER,
            protein INTEGER,
            salt INTEGER
        );
        """
        self.executeQuery(sqlPersonalDiet)
        # create user profile
        sqlUserProfile = """
        CREATE TABLE IF NOT EXISTS userprofiles(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            sex BINERY,
            height FLOAT(10),
            weight FLOAT(10),
            age INT,
            activity INT,
            BMR INT,
            GML INT,
            CalorieDiet INT
        );
        """
        self.executeQuery(sqlUserProfile)
        # create diet profile
        sqlDietProfile =  """
        CREATE TABLE IF NOT EXISTS dietProfile(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            weight FLOAT(10),
            CalorieDiet INT,
            Date DATE,
            FOREIGN KEY (username) REFERENCES userprofiles (username) 
        );
        """
        self.executeQuery(sqlDietProfile)
        # create default user
        self.addUserProfile('Default',0,0,0,0,0,0)
    # create connection to database
    def createConnection():
        connection = None
        try:
            connection = sqlite3.connect("pantryHealth.db")
            print("Connection to SQLite DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")

        return connection
    dbconnection = createConnection()
    
    # create function to execute queries
    def executeQuery(self, query):
        cursor = self.dbconnection.cursor()
        try:
            cursor.execute(query)
            self.dbconnection.commit()
            print("Query executed successfully")
        except Error as e:
            print(f"The error '{e}' occurred")

    # function to get information from database
    def selectQuery(self, sqlQuery):
        cursor = self.dbconnection.cursor()
        result = None
        try:
            cursor.execute(sqlQuery)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"The error '{e}' occurred")
    # add user profile function
    def addUserProfile(self, username, sex, height, weight, age, activity, GML):
        AddUserProfileSQL = f"""
        INSERT INTO userprofiles (
            username,
            sex,
            height,
            weight,
            age,
            activity,
            BMR,
            GML,
            CalorieDiet
        ) VALUES (
        '"""+username+f"""', {sex}, {height}, {weight}, {age}, {activity}, 0, {GML}, 0);"""
        self.executeQuery(AddUserProfileSQL)
        self.calculateBRM(username)
        self.calculateDiet(username)
    # function to calculate BMR
    def calculateBRM(self, username):
        selectSQL = """
            SELECT * FROM userprofiles WHERE username = '"""+username+"""'
        """
        selectment = self.selectQuery(selectSQL)
        print(selectment[0][2])
        print(selectment[0][4])
        print(selectment[0][5])
        print(selectment[0][6])
        if (selectment[0][2] == 0):
            BMR = (13.397*selectment[0][4]) + (4.799*selectment[0][3]) - (5.677*selectment[0][5]) + 88.362
        else:
            BMR = (9.247*selectment[0][4]) + (3.098*selectment[0][3]) - (4.330*selectment[0][5]) + 447.593
        insertSQL = f"""
            UPDATE userprofiles SET BMR = {int(BMR)} WHERE username = '"""+username+"""';
        """
        self.executeQuery(insertSQL)
    # function to calculate caloric intake of diet
    def calculateDiet(self, username):
        
        selectSQL = """
            SELECT * FROM userprofiles WHERE username = '"""+username+"""'
        """
        DietCalc = 0
        selectment = self.selectQuery(selectSQL)
        
        if (selectment[0][8] == 1):
            DietCalc = selectment[0][7] * (1.1+(selectment[0][6]/10))-500
        elif (selectment[0][8] == 2):
            DietCalc = selectment[0][7] * (1.1+(selectment[0][6]/10))
        elif (selectment[0][8] == 3):
            DietCalc = selectment[0][7] * (1.1+(selectment[0][6]/10))+500
        print(DietCalc)
        insertSQL = f"""
            UPDATE userprofiles SET CalorieDiet = {int(DietCalc)} WHERE username = '"""+username+"""';
        """
        self.executeQuery(insertSQL)
    # add foodtype function
    def addFoodtype(self, name, caloricValue, energyValue, fatValue, fatSaturatedValue, carbohydrateValue, carboSugarValue, fibre, protein, salt):
        unformatAddFoodtype = """
        INSERT INTO foodtype (
            name,
            caloricValue,
            energyValue,
            fatValue,
            fatSaturatedValue,
            carbohydrateValue,
            carboSugarValue,
            fibre,
            protein,
            salt
        ) VALUES (
        '"""+name+"""', {}, {}, {}, {}, {}, {}, {}, {}, {})"""
        sqlAddFoodtypeString = unformatAddFoodtype.format(caloricValue, energyValue, fatValue, fatSaturatedValue, carbohydrateValue, carboSugarValue, fibre, protein, salt)
        try:
            self.executeQuery(sqlAddFoodtypeString)
        except:
            print("Duplicate food type")
    # remove foodtype function
    def removeFoodtype(self, name):
        sqlstatement = """
        DELETE FROM foodtype WHERE name = '"""+name+"""'
        """
        self.executeQuery(sqlstatement)
    # set current day diet
    def setCurrentDayDiet(self):
        sqlSetDiet = """
            INSERT INTO diet (
            username,
            date,
            caloricValue,
            energyValue,
            fatValue,
            fatSaturatedValue,
            carbohydrateValue,
            carboSugarValue,
            fibre,
            protein,
            salt
            ) VALUES (
        '"""+self.username+"""', CURRENT_DATE, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        """
        try:
            self.executeQuery(self.dbconnection, sqlSetDiet)
        except:
            print("Error")
    # add to diet 
    def addDietIntake(self, username, typename, number):
        unformatAddtoDiet = """
        UPDATE diet SET """+typename+"""" = {}
        WHERE date = CURRENT_DATE
        """
        sqlGetNumber = """
        SELECT """+typename+"""" FROM diet WHERE date = CURRENT_DATE
        """
        currentNumber = self.selectQuery(self.dbconnection,sqlGetNumber)
        newNumber = currentNumber + number
        sqlAddtoDiet = unformatAddtoDiet.format(newNumber)
        try:
            self.executeQuery(self.dbconnection, sqlAddtoDiet)
        except:
            print("Error")
    # add to weight progress
    def addWeightProgress(self, username, value):
        selectionSQL = "SELECT CalorieDiet FROM userprofiles WHERE username = '"+username+"'"
        selectionCalorieDiet = self.selectQuery(selectionSQL)
        AddWeightProgess = """
        INSERT INTO dietProfile (
            username,
            weight,
            CalorieDiet,
            Date
        ) VALUES (
            '"""+username+f"""', {value},{selectionCalorieDiet[0][0]}, CURRENT_DATE
        )
        """
        try:
            self.executeQuery(AddWeightProgess)
        except:
            print("Error")
    # add food to pantry function
    def addFoodItem(self, name, foodID, expiryDate, quantity):
        unformatedsqlAddFoodItem = """
            INSERT INTO pantry (
                name,
                foodtypeID,
                expiryDate,
                quantity
            ) VALUES (
            '"""+name+"""', {}, """+expiryDate+""", {}
            )
        """
        sqlAddFoodItem = unformatedsqlAddFoodItem.format(foodID,quantity)
        try:
            self.executeQuery(sqlAddFoodItem)
        except:
            print("Failed to add food item")
    # remove food item from pantry
    def removeFoodItem(self,id):
        sqlRemoveFoodItem = """
            DELETE FROM pantry WHERE id = '{}'
        """
        print(id)
        self.executeQuery(sqlRemoveFoodItem.format(id))
    # add or remove a quantity of food from pantry
    def updateFoodQuantity(self,id,quantity):
        unformatedsqlUpdateFoodQuantity = """
            UPDATE pantry SET quantity = {}
            WHERE id = {}
        """
        sqlGetCurrentQuantity = f"SELECT quantity FROM pantry WHERE id = {id}"
        currentQuantity = self.selectQuery(sqlGetCurrentQuantity)
        print(currentQuantity[0][0])
        newQuantity = currentQuantity[0][0] + int(quantity)
        if newQuantity <= 0:
            self.removeFoodItem(id)
        else:
            sqlUpdateQuery = unformatedsqlUpdateFoodQuantity.format(newQuantity,id)
            self.executeQuery(sqlUpdateQuery)
    # update user weight
    def updatePersonalWeight(self,username,weight):
        sqlUpdateQuery = f"""
            UPDATE userprofiles SET weight = {weight}
            WHERE username = '"""+username+"""';"""
        self.executeQuery(sqlUpdateQuery)
    # update user activity
    def updatePersonalActivity(self,username,value):
        sqlUpdateQuery = f"""
            UPDATE userprofiles SET activity = {value}
            WHERE username = '"""+username+"""';"""
        self.executeQuery(sqlUpdateQuery)
    # select all pantry items
    def selectAllPantry(self):
        sqlStatement = "SELECT * FROM pantry"
        selectAll = self.selectQuery(sqlStatement)
        return selectAll
    # select all food tpyes
    def selectAllFoodtype(self):
        sqlStatement = "SELECT * FROM foodtype"
        selectAll = self.selectQuery(sqlStatement)
        return selectAll       
    # select food type id from name
    def selectFoodtypeID(self, name):
        sqlStatement = """
            SELECT id from foodtype WHERE name = '"""+name+"""'
        """
        try:
            id = self.selectQuery(sqlStatement)
            print(id[0][0])
            return id[0][0]
        except:
            print("Error")    
    # select food type name from id
    def selectFoodtypeName(self, id):
        sqlStatement = """
            SELECT name from foodtype WHERE id = {}
        """
        try:
            name = self.selectQuery(sqlStatement.format(id))
            print(name[0][0])
            return name[0][0]
        except:
            print("Error")
    # test statement
    def teststatement(self):            
        sqlSelectFoodtypes = "SELECT * FROM pantry"
        foodtypes = self.selectQuery(sqlSelectFoodtypes)
        for x in foodtypes:
            print(x)
    def teststatement2(self):            
        sqlSelectFoodtypes = "SELECT * FROM foodtype"
        foodtypes = self.selectQuery(sqlSelectFoodtypes)
        for x in foodtypes:
            print(x)
    # class destructor
    def _del_(self):
        self.dbconnection.close()

# class to calculate and track ongoing dietary requiremnts
class dietCalculator:
    def __init__(self, sex, height, weight, age, activity):
        self.sex = sex
        self.height = height
        self.weight = weight
        self.age = age
        self.activity = activity
        self.DMR = self.calculateAveCaloric()
        self.CarbValue = self.calculateValue(45)/4
        self.fatValue = self.calculateValue(25)/9
        self.proteinValue = self.calculateValue(30)/4
        self.fibreValue = 30
        self.saltValue = 6
    
    # calculate needed caloric intake to maintain weight
    def calculateAveCaloric(self):
        # Mifflin-St Jeor Equation
        if (self.sex == 0):
            MSJDMR = (10*self.weight) + (6.25*self.height) - (5*self.age) - 5
        else:
            MSJDMR = (10*self.weight) + (6.25*self.height) - (5*self.age) - 161
        # Revised Harris-Benedict Equation
        if (self.sex == 0):
            RHBDMR = (13.397*self.weight) + (4.799*self.height) - (5.677*self.age) + 88.362
        else:
            RHBDMR = (9.247*self.weight) + (3.098*self.height) - (4.33*self.age) + 447.593
        DMR = (MSJDMR+RHBDMR)/2
        DMR = DMR*self.activity
        return DMR
    def calculateValue(self, perctenage):
        intake = self.DMR * (perctenage/100)
        return intake
    
class userInterface:
    def __init__(self, root, database):
        self.database = database
        root.title("Diet Pantry User Interface")
        # main frame setup
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(1, weight=1)
        # personal frame
        personalframe = ttk.Labelframe(root, text='Personal Details', padding='5')
        personalframe.grid(column=0, row=0, columnspan=2,sticky="nwes")
        # pantry frame
        pantryframe = ttk.Labelframe(root, text='Pantry', padding="5")
        pantryframe.grid(column=0, row=1, sticky="nwes")
        # foodtype frame
        foodtypeframe = ttk.Labelframe(root, text="Food Type", padding="5")
        foodtypeframe.grid(column=1, row=1,sticky="nwes")
        # weight tracker frame
        weightTrackerFrame = ttk.Labelframe(root, text="Diet Progress", padding="5")
        weightTrackerFrame.grid(column=2, row=0, rowspan=2, sticky="nwes")
        # personal details setup
        self.currentUser = "Default"
        sqlStatement = "SELECT * FROM userprofiles WHERE username = '"+self.currentUser+"'"
        self.userdata = database.selectQuery(sqlStatement)
        # weight progress detail setup
        self.weightPoints = []
        self.updateWeightProgressData()
        # personal detail labels
        self.userLabel = ttk.Label(personalframe, text=f'Username: {self.userdata[0][1]}')
        self.userLabel.grid(column=1, row=1,sticky="nwes")
        self.sexLabel = ttk.Label(personalframe, text=f'Sex: {self.userdata[0][2]}')
        self.sexLabel.grid(column=2, row=1,sticky="nwes")
        self.heightLabel = ttk.Label(personalframe, text=f'Height: {self.userdata[0][3]}')
        self.heightLabel.grid(column=3, row=1,sticky="nwes")
        self.weightLabel = ttk.Label(personalframe, text=f'Weight: {self.userdata[0][4]}')
        self.weightLabel.grid(column=4, row=1,sticky="nwes")
        self.ageLabel = ttk.Label(personalframe, text=f'Age: {self.userdata[0][5]}')
        self.ageLabel.grid(column=1, row=2,sticky="nwes")
        self.activityLabel = ttk.Label(personalframe, text=f'Activity: {self.userdata[0][6]}')
        self.activityLabel.grid(column=2, row=2,sticky="nwes")
        self.BMRLabel = ttk.Label(personalframe, text=f'BMR: {self.userdata[0][7]}')
        self.BMRLabel.grid(column=3, row=2,sticky="nwes")
        self.GMLLabel = ttk.Label(personalframe, text=f'GML: {self.userdata[0][8]}')
        self.GMLLabel.grid(column=4, row=2,sticky="nwes")
        self.DietCalcLabel = ttk.Label(personalframe, text=f'Calorie: {self.userdata[0][9]}')
        self.DietCalcLabel.grid(column=5, row=1,sticky="nwes")
        # pantry list
        self.pantrylist = database.selectAllPantry()
        self.pantrylistvar = StringVar(value=self.pantrylist)
        self.pantryListBox = Listbox(pantryframe, listvariable=self.pantrylistvar, selectmode=BROWSE)
        self.pantryListBox.grid(column=1, row=0, columnspan=6,sticky="nwes")
        # pantry frame scrollbar
        pantryScrollbar = ttk.Scrollbar(pantryframe, orient=VERTICAL, command=self.pantryListBox.yview)
        pantryScrollbar.grid(column=0, row=0, sticky='ns')
        self.pantryListBox['yscrollcommand'] = pantryScrollbar.set
        # foodtype frame
        self.foodtypelist = database.selectAllFoodtype()
        self.foodtypelistvar = StringVar(value=self.foodtypelist)
        self.foodtypeListBox = Listbox(foodtypeframe, listvariable=self.foodtypelistvar, selectmode=BROWSE)
        self.foodtypeListBox.grid(column = 0, row = 0, columnspan=7, sticky='nwes')
        # foodtype frame scrollbar
        foodtypeScrollbar = ttk.Scrollbar(foodtypeframe, orient=VERTICAL, command=self.foodtypeListBox.yview)
        foodtypeScrollbar.grid(column=7, row=0, sticky='ns')
        self.foodtypeListBox['yscrollcommand'] = foodtypeScrollbar.set
        # profile buttons
        # add user profile button
        addUserProfileButton = ttk.Button(personalframe, text='Add User Profile', command=self.addUserProfileButton)
        addUserProfileButton.grid(column = 1, row = 0, columnspan=2, sticky=(W,E))
        # switch user profile button
        switchUserProfileButton = ttk.Button(personalframe, text='Swtich User Profile', command=self.switchUserProfileButton)
        switchUserProfileButton.grid(column = 3, row = 0, columnspan=2, sticky=(W,E))
        # update weight button
        updateWeightButton = ttk.Button(personalframe, text='Update Weight', command=self.updateUserWeightButton)
        updateWeightButton.grid(column = 7, row = 0, sticky=(W,E))
        # update activity button
        updateActivityButton = ttk.Button(personalframe, text='Update Activity', command=self.updateUserActivityButton)
        updateActivityButton.grid(column=5, row=0, sticky=(W,E))
        # pantry buttons
        # add to pantry button
        addPantrybutton = ttk.Button(pantryframe, text='Add Pantry Item', command=self.addpantryitem)
        addPantrybutton.grid(column = 1, row = 3, columnspan=3, sticky=(W,E))
        # remove from pantry button
        removePantrybutton = ttk.Button(pantryframe, text='Remove Pantry Item', command=self.removeFooditem)
        removePantrybutton.grid(column = 4, row = 3, columnspan=3, sticky=(W,E))
        # add quantity to pantry item button
        addPantryQuanityButton = ttk.Button(pantryframe, text='Add to Quantity', command=self.addPantryQuantity)
        addPantryQuanityButton.grid(column = 1, row = 4, columnspan=3, sticky=(W,E))
        # remove quantity from pantry item button
        removePantryQuanityButton = ttk.Button(pantryframe, text='Remove Quantity', command=self.decreaseFooditem)
        removePantryQuanityButton.grid(column = 4, row = 4, columnspan=3, sticky=(W,E))
        # food type buttons
        # add food type button
        addFoodtypebutton = ttk.Button(foodtypeframe, text='Add Food Type', command=self.addfoodtype)
        addFoodtypebutton.grid(column = 1, row = 3, columnspan=3, sticky=(W,E))
        # remove food type button
        removeFoodtypebutton = ttk.Button(foodtypeframe, text='Remove Food Type', command=self.removeFoodtype, style='Emergency.TButton')
        removeFoodtypebutton.grid(column = 4, row = 3, columnspan=3, sticky=(W,E))
        # weight progress canvas
        h = ttk.Scrollbar(root, orient=HORIZONTAL)
        v = ttk.Scrollbar(root, orient=VERTICAL)
        weightProgress = WeightProgress(weightTrackerFrame, scrollregion=(0, 0, 1000, 1000), yscrollcommand=v.set, xscrollcommand=h.set)
        weightProgress.grid(column=2, row=0, sticky="nwes", rowspan=2)
        h['command'] = weightProgress.xview
        v['command'] = weightProgress.yview
        # weight progress scroll bar
        
    # function for button to add user profile
    def addUserProfileButton(self):
        # username dialogue box
        usernameDialog = CustomDialogEntry(root, "Input Username")
        root.wait_window(usernameDialog.top)
        username = usernameDialog.dialogueEntryValue
        print("Username :", usernameDialog.dialogueEntryValue)
        # sex dialogue box
        sexDialog = CustomDialogChoice(root, "What is your Sex?", "Male", "Female")
        root.wait_window(sexDialog.top)
        if sexDialog.dialogueChoiceValue == 1:
            sex = 0
        else:
            sex = 1
        print(sex)
        # height dialogue box
        heightDialog = CustomDialogEntry(root, "Input Height in cm")
        root.wait_window(heightDialog.top)
        height = heightDialog.dialogueEntryValue
        # weight dialogue box
        weightDialog = CustomDialogEntry(root, "Input Weight in kg")
        root.wait_window(weightDialog.top)
        weight = weightDialog.dialogueEntryValue
        self.database.addWeightProgress(self.currentUser,int(weight))
        # age dialogue box
        ageDialog = CustomDialogEntry(root, "Input Age")
        root.wait_window(ageDialog.top)
        age = ageDialog.dialogueEntryValue
        # activity dialogue box
        activityDialog = CustomDialogEntry(root, "Input Activty 1 for lowest 6 for highest")
        root.wait_window(activityDialog.top)
        activity = activityDialog.dialogueEntryValue
        GMLDialog = CustomDialog3Choice(root,"Do You Want to Loose or Gain Weight?","Gain Weight","Maintain Weight","Loose Weight")
        root.wait_window(GMLDialog.top)
        GML = GMLDialog.dialogueChoiceValue
        self.database.addUserProfile(username, sex, int(height), int(weight), int(age), int(activity), int(GML))
    # function for button to update user weight
    def updateUserWeightButton(self):
        newWeightDialog = CustomDialogEntry(root, "Input New Weight")
        root.wait_window(newWeightDialog.top)
        newWeight = newWeightDialog.dialogueEntryValue
        print(newWeight)
        self.database.updatePersonalWeight(self.currentUser,newWeight)
        self.database.calculateBRM(self.currentUser)
        self.database.calculateDiet(self.currentUser)
        self.database.addWeightProgress(self.currentUser,newWeight)
        self.updateUserData()
    # function for button to update user activity
    def updateUserActivityButton(self):
        newActivityDialog = CustomDialogEntry(root, "Input Activty 1 for lowest 6 for highest")
        root.wait_window(newActivityDialog.top)
        newActivity = newActivityDialog.dialogueEntryValue
        self.database.updatePersonalActivity(self.currentUser,newActivity)
        self.database.calculateDiet(self.currentUser)
        self.updateUserData()
    # function for button to switch displayed current user
    def switchUserProfileButton(self):
        self.usertop = Toplevel(root)
        sqlGetUserlist = """
        SELECT username FROM userprofiles
        """
        # userprofile list
        self.userlist = self.database.selectQuery(sqlGetUserlist)
        userlistvar = StringVar(value=self.userlist)
        self.userListBox = Listbox(self.usertop, listvariable=userlistvar, selectmode=BROWSE)
        self.userListBox.grid(column=1, row=0, columnspan=6,sticky="nwes")
        # userprofile list scrollbar
        userScrollbar = ttk.Scrollbar(self.usertop, orient=VERTICAL, command=self.userListBox.yview)
        userScrollbar.grid(column=0, row=0, sticky='ns')
        self.userListBox['yscrollcommand'] = userScrollbar.set
        userSubmit = ttk.Button(self.usertop, text='Select', command=self.changeUser)
        userSubmit.grid(column=1,row=1,sticky='nwes')
    # function to change current user
    def changeUser(self):
        idas = self.userListBox.curselection()
        self.currentUser = self.userlist[idas[0]][0]
        self.updateUserData()
        self.usertop.destroy()
    # function to set user data display
    def updateUserData(self):
        sqlStatement = "SELECT * FROM userprofiles WHERE username = '"+self.currentUser+"'"
        self.userdata = self.database.selectQuery(sqlStatement)
        # personal detail labels
        self.userLabel.configure(text=f'Username: {self.userdata[0][1]}')
        self.sexLabel.configure(text=f'Sex: {self.userdata[0][2]}')
        self.heightLabel.configure(text=f'Height: {self.userdata[0][3]}')
        self.weightLabel.configure(text=f'Weight: {self.userdata[0][4]}')
        self.ageLabel.configure(text=f'Age: {self.userdata[0][5]}')
        self.activityLabel.configure(text=f'Activity: {self.userdata[0][6]}')
        self.BMRLabel.configure(text=f'BMR: {self.userdata[0][7]}')
        self.GMLLabel.configure(text=f'GML: {self.userdata[0][8]}')
        self.DietCalcLabel.configure(text=f'Diet: {self.userdata[0][9]}')
    # function to update weight progress data
    def updateWeightProgressData(self):
        self.weightPoints = []
        sqlStatementWeight = "SELECT * FROM dietProfile WHERE username = '"+self.currentUser+"';"
        self.weightSelectment = self.database.selectQuery(sqlStatementWeight)
        print(self.weightSelectment)
    # function for button to remove food types
    def removeFoodtype(self):
        selectedFoodtypeID = self.foodtypeListBox.curselection()
        if selectedFoodtypeID:
            selectedFoodtype = self.foodtypelist[selectedFoodtypeID[0]]
            self.database.removeFoodtype(selectedFoodtype[1])
            self.foodtypelist = self.database.selectAllFoodtype()
            self.foodtypelistvar.set(self.foodtypelist)
    # function for button to remove food item
    def removeFooditem(self):
        selectedItemID = self.pantryListBox.curselection()
        if selectedItemID:
            selectedItem = self.pantrylist[selectedItemID[0]]
            self.database.removeFoodItem(selectedItem[0])
            self.pantrylist = self.database.selectAllPantry()
            self.pantrylistvar.set(self.pantrylist)
    # function for button to increase quantity of food item
    def addPantryQuantity(self):
        # dialogue box
        quantityDialog = CustomDialogEntry(root, "Input quantity")
        root.wait_window(quantityDialog.top)
        quantity = quantityDialog.dialogueEntryValue
        selectedItemID = self.pantryListBox.curselection()
        if selectedItemID:
            selectedItem = self.pantrylist[selectedItemID[0]]
            self.database.updateFoodQuantity(selectedItem[0],quantity)
            self.pantrylist = self.database.selectAllPantry()
            self.pantrylistvar.set(self.pantrylist)
    # function for button to decrease quantity of food item
    def decreaseFooditem(self):
        # dialogue box
        quantityDialog = CustomDialogEntry(root, "Input quantity to remove")
        root.wait_window(quantityDialog.top)
        quantity = quantityDialog.dialogueEntryValue
        NewQuantity = 0 - int(quantity)
        selectedItemID = self.pantryListBox.curselection()
        if selectedItemID:
            selectedItem = self.pantrylist[selectedItemID[0]]
            self.database.updateFoodQuantity(selectedItem[0],NewQuantity)
            self.pantrylist = self.database.selectAllPantry()
            self.pantrylistvar.set(self.pantrylist)
    # function for button to add food type
    def addfoodtype(self):
        name = simpledialog.askstring("Input", "Enter the food types Name")
        caloricValue = simpledialog.askinteger("Input", "Enter the Caloric Value")
        energyValue = simpledialog.askinteger("Input", "Enter the Energy Value")
        fatValue = simpledialog.askinteger("Input", "Enter the Fat per gram")
        fatSaturatedValue = simpledialog.askinteger("Input", "Enter the saturated fat")
        carbohydrateValue = simpledialog.askinteger("Input", "Enter the Carbohydrate per gram")
        carboSugarValue = simpledialog.askinteger("Input", "Enter the Carbo Sugar")
        fibre = simpledialog.askinteger("Input", "Enter the Fibre per gram")
        protein = simpledialog.askinteger("Input", "Enter the Protein per gram")
        salt = simpledialog.askinteger("Input", "Enter the Salt per gram")
        self.database.addFoodtype(name, caloricValue, energyValue, fatValue, fatSaturatedValue, carbohydrateValue, carboSugarValue, fibre, protein, salt)
        # reset list
        self.foodtypelist = self.database.selectAllFoodtype()
        self.foodtypelistvar.set(self.foodtypelist)
    # function for button to add pantry item
    def addpantryitem(self):
        name = simpledialog.askstring("Input", "Enter the pantry items Name")
        foodtypename = simpledialog.askstring("Input", "Enter the food type Name")
        print(foodtypename)
        foodID = self.database.selectFoodtypeID(foodtypename)
        expiryDate = simpledialog.askstring("Input", "Enter the pantry items expiry date")
        quantity = simpledialog.askinteger("Input", "Enter the quantity in g")
        self.database.addFoodItem(name, foodID, expiryDate, quantity)
        # reset pantry list
        self.pantrylist = self.database.selectAllPantry()
        self.pantrylistvar.set(self.pantrylist)
class CustomDialogEntry():
    def __init__(self, parent, displayText):
        self.top = Toplevel(parent)
        diaLabel = ttk.Label(self.top, text=displayText)
        diaLabel.pack()
        self.diaEntry = ttk.Entry(self.top)
        self.diaEntry.pack()
        diaSubmit = ttk.Button(self.top, text='Submit', command=self.send)
        diaSubmit.pack()
    def send(self):
        self.dialogueEntryValue = self.diaEntry.get()
        self.top.destroy()
class CustomDialogChoice():
    def __init__(self, parent, displayText, choice1, choice2):
        self.top = Toplevel(parent)
        diaLabel = ttk.Label(self.top, text=displayText)
        diaLabel.pack()
        diaButton1 = ttk.Button(self.top, text=choice1, command=self.button1)
        diaButton1.pack()
        diaButton2 = ttk.Button(self.top, text=choice2, command=self.button2)
        diaButton2.pack()
    def button1(self):
        self.dialogueChoiceValue = 1
        self.top.destroy()
    def button2(self):
        self.dialogueChoiceValue = 2
        self.top.destroy()
class CustomDialog3Choice():
    def __init__(self, parent, displayText, choice1, choice2, choice3):
        self.top = Toplevel(parent)
        diaLabel = ttk.Label(self.top, text=displayText)
        diaLabel.pack()
        diaButton1 = ttk.Button(self.top, text=choice1, command=self.button1)
        diaButton1.pack()
        diaButton2 = ttk.Button(self.top, text=choice2, command=self.button2)
        diaButton2.pack()
        diaButton3 = ttk.Button(self.top, text=choice3, command=self.button3)
        diaButton3.pack()
    def button1(self):
        self.dialogueChoiceValue = 1
        self.top.destroy()
    def button2(self):
        self.dialogueChoiceValue = 2
        self.top.destroy()
    def button3(self):
        self.dialogueChoiceValue = 3
        self.top.destroy()
class WeightProgress(Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        for x in range(0,360,20):
            self.create_line(x, 0, x, 350, fill='gray')
        for y in range(0,360,20):
            self.create_line(0, y, 360, y, fill='gray')

root = Tk()

testdatabase = programDatabase('Dave')
testdatabase.teststatement()
testdatabase.teststatement2()
# testdatabase.calculateBRM('J')
userInterface(root, testdatabase)
root.mainloop()

del testdatabase