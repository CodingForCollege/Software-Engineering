import csv
file_name = "User Profile.csv"

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
            

new_user = user_profile()
#new_user.set_weekly_budget(10000)
#new_user.set_weekly_notif_limit(9999)
new_user.add_pm('credit','4565', 50,20)
new_user.add_pm('debit', '8934', 200,100)
new_user.rename_pm('4565', 'Savings')

#new_user.change_pm_budget('4565', 75)

print(new_user.get_pm_name('8934'))
print(new_user.get_pm_budget('4565'))

#new_user.change_pm_aas('8934', 50)
print(new_user.get_pm_aas('8934'))

#new_user.change_pm_aas('8934', 50)
new_user.add_category('4565', 'Miscellaneous', 40, 35)
new_user.add_category('8934', 'Gas', 30, 20)

new_user.add_category('8934','food', 170, 150)

#new_user.change_cat_budget('4565', 'Miscellaneous' ,300)

print(new_user.get_sum_of_pm_budgets())

print(new_user.get_cat_budget('4565', 'Miscellaneous'))

#new_user.change_cat_notif('8934', 'Food', 160)

#new_user.change_cat_AAS('8934', 'Gas', 10)

new_user.transaction_both('4565', 'miscellaneous', 30)
new_user.transaction_both('8934', 'food', 100)


