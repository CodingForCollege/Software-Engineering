# Importing libraries
from flask import Flask, render_template, url_for, request, redirect, jsonify, send_from_directory, flash
import pandas as pd
import imaplib
import email
import yaml  
import re
import bcrypt
import uuid
import os
import csv
import webbrowser
import threading
import shutil


app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flashing messages

#--------------------------------------------------------------------------------------------------------------

# Load user data from CSV (always load fresh data when the app starts or on each login)
def load_user_data(filename='data/users.csv'):
    if not os.path.exists(filename):
        return {}  # If file doesn't exist, return an empty dictionary
    
    user_data = {}
    # If the file exists, load user data from it
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:
                email, hashedPassword = row
                user_data[email] = hashedPassword.encode()  # Convert the hashed password back to bytes
    return user_data

# Save a single user's data to the CSV file (append mode)
def save_user_data(email, hashedPassword, filename='data/users.csv'):
    # Ensure the directory exists
    if not os.path.exists('data'):
        os.makedirs('data')

    # Append new user data to CSV
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([email, hashedPassword.decode()])  # Append new user data to CSV

# Validate email format
def validEmail(email):
    return "@" in email and "." in email

# Validate password length
def validPassword(password):
    return len(password) >= 8

# In-memory storage for users and sessions
def get_user_data():
    return load_user_data()  # Always reload from CSV at app start

userDB = get_user_data()  # Load users from CSV at app start
sessionDB = {}

# Explicitly set the path to 'data' relative to the current script (app.py)
data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

# Ensure the directory for user data exists
os.makedirs(data_folder, exist_ok=True)

#--------------------------------------------------------------------------------------------------------------

# Creates a file for the specific user

'''def userDataAccessKey(email):
    front ="env/data/"
    back = "_data.csv" 
    name = front + email + back
    print(name)   
    return name

def getUserFile(fileName):
    newFile = shutil.copy("env/data/temp.csv", fileName)
    #return newFile'''


#--------------------------------------------------------------------------------------------------------------

with open('env/data/credentials.yml') as f:
    content = f.read()
    
# from credentials.yml import user name and password
my_credentials = yaml.load(content, Loader=yaml.FullLoader)

#Load the user name and passwd from yaml file
user, password = my_credentials["user"], my_credentials["password"] 

#URL for IMAP connection
imap_url = 'imap.gmail.com'

# Connection with GMAIL using SSL
my_mail = imaplib.IMAP4_SSL(imap_url)

# Log in using your credentials
my_mail.login(user, password)

# Select the Inbox to fetch messages
my_mail.select('Inbox')

#Define Key and Value for email search
key = 'FROM'
value = 'amandaarreola@dusty.tamiu.edu'
_, data = my_mail.search(None, key, value)  #Search for emails with specific key and value

mail_id_list = data[0].split()  #IDs of all emails that we want to fetch 

msgs = [] # empty list to capture all messages
#Iterate through messages and extract data into the msgs list
for num in mail_id_list:
    typ, data = my_mail.fetch(num, '(RFC822)') #RFC822 returns whole message (BODY fetches just body)
    msgs.append(data) 
    
#Lists and counters
Parsing_db = {
    "Total": 0,
    "Card": 0,
}
total_list =[]
card_list = []

#Getting the email reciept information
for msg in msgs:
    for response_part in msg:
        if type(response_part) is tuple:
            my_msg=email.message_from_bytes((response_part[1]))
            
            text_content = ""
            html_content = ""
            
            for part in my_msg.walk():
                content_type = part.get_content_type()
                #print(part.get_content_type())
                if part.get_content_type() == 'text/plain':
                     text_content = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
                elif content_type == 'text/html':
                    html_content = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
                    
            # Use text content if available; otherwise, fall back to HTML content
            email_body = text_content if text_content else html_content
                    
            #DO NOT PRINT EMAIL BODY WHEN PRESENTING!!!
            #CONTAINS SENSITIVE INFO!!!
            #print(email_body)

            # Extract the total amount (with alternative names)
            match_total = re.search(r"(Total|TOTAL|Total of Submitted Payments|Amount|Debit|Total Amount|Total Cost|Grand Total):?\s*\$?(\d+\.\d{2})", email_body)
            if match_total:
                total = match_total.group(2)
                total_list.append(total)
            else:
                total_list.append('0')

            # Extract the last four digits of the card (with alternative names)
            match_card = re.search(r"(Ending in\s+\*\s|Ending in\s+\:|Ending in\:\s|Card ending|Mastercard|Credit|Credit Card|Credit Card\s+#\s\*\*\*\*\*\*\*\*\*\*\*\*|\s+\.\.\.\.\s*|Visa\s+\.\.\.|\*\*\*\*\s*)(\d{4})", email_body)
            if match_card:
                card = match_card.group(2) 
                card_list.append(card)
            else:
                card_list.append('0')  

Parsing_db["Total"] = total_list
Parsing_db["Card"] = card_list

#print(total_list)
#print(card_list)

df = pd.DataFrame(Parsing_db)
#print(df)
df.to_csv('env/data/data.csv', index=False)

#--------------------------------------------------------------------------------------------------------------

'''global fn
fn = 'env/data/User Profile.csv'
file_name = fn

def getFile(input):
    file_name = input
    print(file_name)
    file_name = fn
    #return file_name'''


file_name = 'env/static/transactions/UserProfile.csv'


class user_profile:
    
    weekly_budget = 0.00
    weekly_limit = 0.00
    weekly_AAS = 0.00
    sum_of_pm_budgets = 0.00
    #Payment Profile format:
    # ID Numbers : [ Method Name, budget, budget amount spent, (Category Name, Budget limit, Notification limit, Amount spent)]
    # amount spent will have a default of 0
    payment_profiles = {}
    
    #checks if value is negative
    def negative_check(self, value):
        while value < 0:
            #send error message
            print("Value cannot be a negative number. Please enter a positive value: ")
            value = float(input())
        return value
    
    #checks if sub budget value is over super budget
    def over_budget_check(self, og_budget, new_budget):
        while new_budget > og_budget:
            #send error message
            print(f"Value cannot be over ${og_budget}. Enter a new value:")
            new_budget = float(input())
            new_budget = user_profile().negative_check(new_budget)
            
        return new_budget
    
    #sets overall weekly spending budget
    def set_weekly_budget(self, weekly_budget):
        #checks if value is negative
        weekly_budget = user_profile().negative_check(weekly_budget)
        
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)

        # Update the specific cell
        rows[1][0] = weekly_budget

        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
        
    def get_weekly_budget(self):
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            
        return float(rows[1][0])
    
    #sets overall weekly spending notification limit
    def set_weekly_notif_limit(self, notif_limit):
        #checks if notif_limit value is acceptable
        #not negative and within bounds
        notif_limit = user_profile().negative_check(notif_limit)
        weekly_budget = user_profile().get_weekly_budget()
        notif_limit = user_profile().over_budget_check(weekly_budget, notif_limit)
        
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)

        # Update the specific cell
        rows[1][1] = notif_limit

        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
        
    def get_weekly_notif_limit(self):
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        return float(rows[1][1])
    
    def set_weekly_AAS(self, weekly_AAS):
        weekly_AAS = user_profile().negative_check(weekly_AAS)
        weekly_notif_limit = user_profile().get_weekly_notif_limit()
        weekly_budget = user_profile().get_weekly_budget()
        
        og_weekly_AAS = user_profile().get_weekly_AAS()
        
        weekly_AAS = og_weekly_AAS + weekly_AAS
        
        if weekly_AAS > weekly_budget:
            #send notification
            print("Over budget!")
        else:
            if weekly_AAS >= weekly_notif_limit:
                #send out notification
                print(f"Notification amount met! ${weekly_AAS} has been spent out of {weekly_budget}")
                
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)

        # Update the specific cell
        rows[1][2] = weekly_AAS

        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

    def get_weekly_AAS(self):
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            
        return float(rows[1][2])
    
    def get_sum_of_pm_budgets(self):
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            
        return float(rows[1][3])
    
    #add a payment method profile to user account
    def add_pm(self, pay_method, pm_ID, pm_budget, notif_limit):
        pay_method = pay_method.capitalize()
        
        #checks if potential budget value is acceptable
        #not negative and within bounds
        pm_budget = user_profile().negative_check(pm_budget)
        weekly_budget = user_profile().get_weekly_budget()
        pm_budget = user_profile().over_budget_check(weekly_budget, pm_budget)
        
        og_sum_of_budgets = user_profile().get_sum_of_pm_budgets()
        sum_with_new_budget = og_sum_of_budgets + pm_budget
        weekly_budget = user_profile().get_weekly_budget()
        difference = weekly_budget - og_sum_of_budgets
        
        #checks if potential budget fits in weekly budget
        while sum_with_new_budget > weekly_budget:
            #send error message
            print(f"Payment Method budget cannot be greater than {difference} to comply with overall weekly budget of ${weekly_budget}. Please enter a budget value: ")
            pm_budget = float(input())
            sum_with_new_budget = og_sum_of_budgets + pm_budget
        
        notif_limit = user_profile().negative_check(notif_limit)
        notif_limit = user_profile().over_budget_check(pm_budget, notif_limit)
        
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        i = user_profile().get_row_index(pm_ID)    
        
        if i < len(rows):
            rows[i] = [pm_ID, pay_method, pm_budget,notif_limit,0,0]
        else:
            rows.append([pm_ID, pay_method, pm_budget,notif_limit,0,0])
        
        rows[1][3] = sum_with_new_budget
        
        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
  
    #rename payment method profile
    def rename_pm(self, pm_ID, new_name):
        new_name = new_name.capitalize() 
        
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        i = user_profile().get_row_index(pm_ID)
        
        rows[i][1] = new_name    
        
        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
    
    #return the name of the payment method
    def get_pm_name(self, pm_ID):
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        i = user_profile().get_row_index(pm_ID)    
        
        return rows[i][1]
        
    #remove a payment method profile from user account
    def remove_pm(self, pm_ID):
        del user_profile.payment_profiles[pm_ID]

    #set the budget value for a payment method profile
    def change_pm_budget(self, pm_ID, pm_budget):
        #checks if potential budget value is acceptable
        #not negative and within bounds
        pm_budget = user_profile().negative_check(pm_budget)
        weekly_budget = user_profile().get_weekly_budget()
        pm_budget = user_profile().over_budget_check(weekly_budget, pm_budget)
        
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            
        i = user_profile().get_row_index(pm_ID)
        
        rows[i][2] = pm_budget    
        
        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
    
    #return the budget value for a payment method profile
    def get_pm_budget(self, pm_ID):
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        i = user_profile().get_row_index(pm_ID)
        
        return float(rows[i][2])
    
    def change_pm_notif_limit(self, pm_ID, notif_limit):
        notif_limit = user_profile().negative_check(notif_limit)
        pm_budget = user_profile().get_pm_budget(pm_ID)
        notif_limit = user_profile().over_budget_check(pm_budget, notif_limit)
        
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        i = user_profile().get_row_index(pm_ID)
        
        rows[i][3] = notif_limit
        
        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
    
    def get_pm_notif_limit(self, pm_ID):
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        i = user_profile().get_row_index(pm_ID)
        
        return float(rows[i][3])
    
    #add value of "amount spent" to the amount already spent value of a payment method
    def change_pm_aas(self, pm_ID, amount_spent):
        
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            
        i = user_profile().get_row_index(pm_ID)
        
        Aas = user_profile().get_pm_aas(pm_ID)
        
        rows[i][4] = amount_spent +Aas
        
        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
    
    #return the amount already spent value of a payment method profile
    def get_pm_aas(self, pm_ID):
        
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        i = user_profile().get_row_index(pm_ID)
        
        return float(rows[i][4])
    
    def get_sum_of_cat_budgets(self, pm_ID):
        
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            
        i = user_profile().get_row_index(pm_ID)
    
        return float(rows[i][5])
    
    #adds a category profile for a payment method profile
    def add_category(self, pm_ID, cat, cat_budget, notif_limit):
        cat = cat.capitalize()
        #checks if cat_budget value is acceptable
        #not negative and within bounds
        cat_budget = user_profile().negative_check(cat_budget)
        
        pm_budget = user_profile().get_pm_budget(pm_ID)
        cat_budget = user_profile().over_budget_check(pm_budget, cat_budget)
        
        og_sum_of_budgets = user_profile().get_sum_of_cat_budgets(pm_ID)
        sum_with_new_budget = og_sum_of_budgets + cat_budget
        pm_budget = user_profile().get_pm_budget(pm_ID)
        difference = pm_budget - og_sum_of_budgets
        
        cat_index = user_profile().get_cat_column_index(pm_ID,cat)
        
        #checks if potential budget fits in weekly budget
        while sum_with_new_budget > pm_budget:
            #send error message
            print(f"Payment Method budget cannot be greater than {difference} to comply with overall weekly budget of ${pm_budget}. Please enter a budget value: ")
            cat_budget = float(input())
            sum_with_new_budget = og_sum_of_budgets + cat_budget
        
        #checks if notif_limit value is acceptable
        #not negative and within bounds
        notif_limit = user_profile().negative_check(notif_limit)
        notif_limit = user_profile().over_budget_check(cat_budget, notif_limit)
        
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        i = user_profile().get_row_index(pm_ID)
        
        rows[i].append(cat)
        rows[i].append(cat_budget)
        rows[i].append(notif_limit)
        rows[i].append(0)
        
        rows[i][5] = sum_with_new_budget
        
        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

    #return the index of the category profile in the list to use in other functions
    def get_cat_column_index(self, pm_ID, cat):
                
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        i = user_profile().get_row_index(pm_ID)
        c_i = 6
        row_tot_index = len(rows[i])
        
        while c_i < row_tot_index:
            if rows[i][c_i] == cat:
                break
            c_i = c_i + 4
        
        return c_i
        
    #delete a category profile from a payment method profile
    def remove_category(self, pm_ID, cat):
        cat = cat.capitalize()
        #cat_index = user_profile().get_cat_column_index(pm_ID, cat)
        #del user_profile.payment_profiles[pm_ID][cat_index]
    
    #set the budget value for a category profile
    def change_cat_budget(self, pm_ID,cat, budget):
        cat = cat.capitalize()
        cat_index = user_profile().get_cat_column_index( pm_ID, cat)
        #checks if cat_budget value is acceptable
        #not negative and within bounds
        budget = user_profile().negative_check(budget)
        
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        i = user_profile().get_row_index(pm_ID)
        
        pm_budget = float(rows[i][2])
        
        budget = user_profile().over_budget_check(pm_budget, budget)
        
        rows[i][cat_index+1] = budget
        
        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
    
    #return the budget value for a category profile
    def get_cat_budget(self, pm_ID, cat):
        cat = cat.capitalize()
        cat_index = user_profile().get_cat_column_index(pm_ID, cat)
        
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        i = user_profile().get_row_index(pm_ID)
        
        return float(rows[i][cat_index+1])
    
    #set the notification limit for a category profile
    def change_cat_notif(self, pm_ID,cat, notif_limit):
        cat = cat.capitalize()
        cat_index = user_profile().get_cat_column_index(pm_ID,cat)
        #checks if notif_limit value is acceptable
        #not negative and within bounds
        notif_limit = user_profile().negative_check(notif_limit)
        cat_budget = user_profile().get_cat_budget(pm_ID, cat)
        notif_limit = user_profile().over_budget_check(cat_budget, notif_limit)
        
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        i = user_profile().get_row_index(pm_ID)
        
        rows[i][cat_index+2] = notif_limit
        
        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
        
        #user_profile.payment_profiles[pm_ID][cat_index][2] = notif_limit
        
    #return the notification limit for a category profile
    def get_cat_notif(self, pm_ID,cat):
        cat = cat.capitalize()
        cat_index = user_profile().get_cat_column_index(pm_ID,cat)
        
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        i = user_profile().get_row_index(pm_ID)
        
        return float(rows[i][cat_index+2])
    
    #set the amount already spent value of a category profile
    def change_cat_AAS(self, pm_ID,cat,amount_spent):
        cat = cat.capitalize()
        cat_index = user_profile().get_cat_column_index(pm_ID,cat)
        
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            
        i = user_profile().get_row_index(pm_ID)
        
        Aas = user_profile().get_cat_AAS(pm_ID, cat)
        
        rows[i][cat_index+3] = amount_spent +Aas
        
        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
        
    #return the amount already spent value of a category profile
    def get_cat_AAS(self, pm_ID, cat):
        cat = cat.capitalize()
        cat_index = user_profile().get_cat_column_index(pm_ID,cat)
        
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        i = user_profile().get_row_index(pm_ID)
        
        return float(rows[i][cat_index+3])
    
    #adds the amount spent on a transaction to the corresponding amount already spent value of a category
    #checks if new amount already spent value is above the notification limit for the category
    #checks if new amount already spent value isa above the budget limit for the category
    #sends notificaiton if either of the last two condictions are met
    def transaction_on_cat(self, pm_ID, cat, amount_spent):
        cat = cat.capitalize()
        #adds transaction amount to amount already spent for the category profile
        user_profile().change_cat_AAS(pm_ID, cat, amount_spent)
        #gets new amount already spent value
        cat_aas = user_profile().get_cat_AAS(pm_ID, cat)
        #gets notification limit for category
        cat_notif_limit = user_profile().get_cat_notif(pm_ID, cat)
        #gets budget for category
        cat_budget = user_profile().get_cat_budget(pm_ID, cat)
        
        if cat_aas >= cat_notif_limit:
            #send notification code here
            print(f"Warning, limit has been reached for {cat}! Current amount spent is: {cat_aas}")
        
        if cat_aas >= cat_budget:
            #send notification code here
            print(f"Budget limit reached. Stop spending on {cat}!")
            if cat_aas > cat_budget:
                difference = cat_aas-cat_budget
                print(f"${difference} spent over budget.")
    
    #adds the amount spent on a transaction to the corresponding amount already spent value of a payment method profile
    #checks if new amount already spent value is above the budget limit for the payment method profile
    #sends notificaiton if either of the last two condictions are met
    def transaction_on_pm(self, pm_ID, amount_spent):
        #adds transaction amount to amount already spent for the payment method
        user_profile().change_pm_aas(pm_ID, amount_spent)
        #gets new amount already spent value
        pm_aas = user_profile().get_pm_aas(pm_ID)
        #gets notification limit for pm
        pm_notif_limit = user_profile().get_pm_notif_limit(pm_ID)
        #gets pm budget
        pm_budget = user_profile().get_pm_budget(pm_ID)
        #gets pm name
        pm_name = user_profile().get_pm_name(pm_ID)
        
        if pm_aas >= pm_notif_limit:
            #send notification code here
            print(f"Warning, limit has been reached for {pm_name}! Current amount spent is: {pm_aas}")
        
        if pm_aas >= pm_budget:
            #send notification here
            print(f"Budget limit reached. Stop spending using account ending in X{pm_ID}")
    
    #performs transaction on both
    def transaction_both(self, pm_ID, cat, amount_spent):
        user_profile().transaction_on_cat(pm_ID, cat, amount_spent)
        user_profile().transaction_on_pm(pm_ID, amount_spent)
        user_profile().set_weekly_AAS(amount_spent)
        
    def get_row_index(self, pm_ID):
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            i = 0
            for row in rows:
                if row[0] == pm_ID:
                    break
                i = i+1
        
        return i

#--------------------------------------------------------------------------------------------------------------

#Using Email Parsing
new_user = user_profile()

'''new_user.add_pm('debit', '0024', 500, 450)
new_user.add_category('0024', 'Groceries', 150, 50)
new_user.add_pm('credit', '1773', 500, 450)
new_user.add_category('1773', 'Recreational', 150, 50)
new_user.add_pm('debit', '1833', 500, 450)
new_user.add_category('1833', 'Shopping', 150, 50)
new_user.add_pm('credit', '0', 500, 450)
new_user.add_category('0', 'Utilities', 150, 50)'''

for i in range(len(total_list)):
    new_user.transaction_on_pm(card_list[i], float(total_list[i]))

#--------------------------------------------------------------------------------------------------------------

# Returns true if password is 8 chars long
def validPassword(password):
    return len(password) >= 8

# Register route (handles POST for registration and GET to show the form)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        # Reload user data fresh from the CSV file before checking for email duplicates
        userDB = load_user_data()  # Always reload fresh data from CSV

        # Check if email is already in userDB (CSV)
        if email in userDB:
            return jsonify({"message": "User already exists. Try logging in or use a different email."}), 400

        if not validEmail(email):
            return jsonify({"message": "Invalid email format. Please try again."}), 400

        if not validPassword(password):
            return jsonify({"message": "Password must be at least 8 characters long. Please try again."}), 400

        # Hash the password and save the user in memory
        hashedPassword = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        # Save the new user to the CSV file
        save_user_data(email, hashedPassword)

        return jsonify({"message": "User registered successfully!"}), 201

    # If it's a GET request, render the register page
    return render_template('register.html')

# Login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # Reload user data fresh from the CSV file (always do this at login attempt)
    global userDB
    userDB = load_user_data()  # This loads the latest user data from the CSV file

    if email not in userDB:
        return jsonify({"message": "User not found. Please register first."}), 404

    storedPassword = userDB[email]

    if bcrypt.checkpw(password.encode(), storedPassword):

        sessionID = str(uuid.uuid4())
        sessionDB[sessionID] = email
        return jsonify({"message": "Login successful!", "sessionID": sessionID}), 200
    else:
        return jsonify({"message": "Invalid password. Please try again."}), 401

# Home route (login page)
@app.route('/')
def index():
    return render_template('index.html')

# Function to open the browser automatically when the app starts
def open_browser():
    try:
        webbrowser.open("http://127.0.0.1:5000/")  # Open the default browser
    except Exception as e:
        print(f"Error occurred while opening the browser: {e}")


@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/budget')
def budget():
    return render_template('budget.html')

@app.route('/budget', methods=['POST'])
def budgetIn():
    
    if request.method == 'POST':
        paymentMethod = request.form.get('paymentMethod')
        paymentBudget = request.form.get('paymentBudget')
        cardNum = request.form.get('cardNum')
        pmNotif = request.form.get('pmNotif')

        categoryCardNumber = request.form.get('categoryCardNumber')
        spendingCategory = request.form.get('spendingCategory')
        categoryBudget = request.form.get('categoryBudget')
        spNotif = request.form.get('spNotif')

        if type(paymentBudget) is not type(None):
            paymentBudget = float(paymentBudget)
            pmNotif = float(pmNotif)
            new_user.add_pm(paymentMethod, cardNum, paymentBudget, pmNotif)


        if type(categoryBudget) is not type(None): 
            categoryBudget = float(categoryBudget)
            spNotif = float(spNotif)
            new_user.add_category(categoryCardNumber, spendingCategory, categoryBudget, spNotif)

    return render_template('budget.html')

@app.route('/transactions')
def transactions():
    return render_template('transactions.html')

@app.route('/transactions/<filename>')
def serve_csv(filename):
    # Ensure the path to 'static/transactions' matches your folder structure
    return send_from_directory('static/transactions', filename)

#--------------------------------------------------------------------------------------------------------------

# Run the Flask app in a separate thread and open the browser automatically
if __name__ == '__main__':
    # Start the Flask app in a separate thread
    def start_server():
        global userDB  # Make sure userDB is global and accessible for updating on each app start
        userDB = load_user_data()  # Reload userDB from CSV at the start of each app run
        app.run(debug=True, use_reloader=False)  # Disable the reloader to avoid multiple restarts

    threading.Thread(target=start_server).start()

    # Open the browser after server starts
    open_browser()
