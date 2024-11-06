#new_user_profile = { 'weekly_budget': 0.00 ,'payment_profiles': {}}
#Payment Profile format:
# Method Name : [ id numbers, budget, budget amount spent, (Category Name, Budget limit, Notification limit, Amount spent)]
# amount spent will have a default of 0
#id numbers = last four numbers of account/card

loop_response = 'n'

class user_profile:
    
    weekly_budget = 0.00
    weekly_limit = 0.00
    weekly_AAS = 0.00
    sum_of_pm_budgets = 0.00
    #Payment Profile format:
    # Method Name : [ id numbers, budget, budget amount spent, (Category Name, Budget limit, Notification limit, Amount spent)]
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
        user_profile.weekly_budget = weekly_budget
    
    
    #sets overall weekly spending notification limit
    def set_weekly_notif_limit(self, notif_limit):
        #checks if notif_limit value is acceptable
        #not negative and within bounds
        notif_limit = user_profile().negative_check(notif_limit)
        notif_limit = user_profile().over_budget_check(user_profile.weekly_budget, notif_limit)
        user_profile.weekly_limit = notif_limit
    
    
    #add a payment method profile to user account
    def add_pm(self, pay_method, id_numbers, pm_budget):
        pay_method = pay_method.capitalize()
        
        #checks if potential budget value is acceptable
        #not negative and within bounds
        pm_budget = user_profile().negative_check(pm_budget)
        pm_budget = user_profile().over_budget_check(user_profile.weekly_budget, pm_budget)
        
        sum_with_new_budget = user_profile.sum_of_pm_budgets + pm_budget
        difference = user_profile.weekly_budget - user_profile.sum_of_pm_budgets
        
        #checks if potential budget fits in weekly budget
        if sum_with_new_budget > user_profile.weekly_budget:
            #send error message
            print(f"Payment Method budget cannot be greater than {difference} to comply with overall weekly budget of ${user_profile.weekly_budget}. Please enter a budget value: ")
            pm_budget = float(input())
        
        user_profile.payment_profiles[pay_method] = [ id_numbers, pm_budget, 0]
  
    #rename payment method profile
    def rename_pm(self, pay_method, new_name):
        new_name = new_name.capitalize()
        pay_method = pay_method.capitalize()
        user_profile.payment_profiles[new_name] = user_profile.payment_profiles[pay_method]
        del user_profile.payment_profiles[pay_method]

    
    #remove a payment method profile from user account
    def remove_pm(self, pay_method):
        pay_method = pay_method.capitalize()
        del user_profile.payment_profiles[pay_method]


    #set the budget value for a payment method profile
    def change_pm_budget(self, pay_method, pm_budget):
        pay_method = pay_method.capitalize()
        #checks if potential budget value is acceptable
        #not negative and within bounds
        pm_budget = user_profile().negative_check(pm_budget)
        pm_budget = user_profile().over_budget_check(user_profile.weekly_budget, pm_budget)
        user_profile.payment_profiles[pay_method][1] = pm_budget
    
        
    #return the budget value for a payment method profile
    def get_pm_budget(self, pay_method):
        pay_method = pay_method.capitalize()
        return user_profile.payment_profiles[pay_method][1]
    
    
    #add value of "amount spent" to the amount already spent value of a payment method
    def change_pm_aas(self, pay_method, amount_spent):
        pay_method = pay_method.capitalize()
        user_profile.payment_profiles[pay_method][2] += amount_spent
    
    
    #return the amount already spent value of a payment method profile
    def get_pm_aas(self, pay_method):
        pay_method = pay_method.capitalize()
        return user_profile.payment_profiles[pay_method][2]
    
    
    #adds a category profile for a payment method profile
    def add_category(self, pay_method, cat, cat_budget, notif_limit):
        pay_method = pay_method.capitalize()
        cat = cat.capitalize()
        #checks if cat_budget value is acceptable
        #not negative and within bounds
        cat_budget = user_profile().negative_check(cat_budget)
        if cat_budget > user_profile.payment_profiles[pay_method][1]:
            cat_budget = user_profile().over_budget_check(user_profile.payment_profiles[pay_method][1], cat_budget)
        
        #checks if notif_limit value is acceptable
        #not negative and within bounds
        notif_limit = user_profile().negative_check(notif_limit)
        notif_limit = user_profile().over_budget_check(cat_budget, notif_limit)
        
        user_profile.payment_profiles[pay_method].append([cat, cat_budget, notif_limit, 0])


    #return the index of the category profile in the list to use in other functions
    def get_cat_index(self, pay_method, cat):
        pay_method = pay_method.capitalize()
        cat = cat.capitalize()
        cat_index = 0
        cat_profiles = user_profile.payment_profiles[pay_method]
        cat_profiles = cat_profiles[3:]
    
        for profile in cat_profiles:
            if profile[0] == cat:
                cat_index = cat_profiles.index(profile)
        return cat_index +3
    
    
    #delete a category profile from a payment method profile
    def remove_category(self, pay_method, cat):
        pay_method = pay_method.capitalize()
        cat = cat.capitalize()
        cat_index = user_profile().get_cat_index(pay_method, cat)
        del user_profile.payment_profiles[pay_method][cat_index]
    
    
    #set the budget value for a category profile
    def change_cat_budget(self, pay_method,cat, budget):
        pay_method = pay_method.capitalize()
        cat = cat.capitalize()
        cat_index = user_profile().get_cat_index( pay_method, cat)
        #checks if cat_budget value is acceptable
        #not negative and within bounds
        budget = user_profile().negative_check(budget)
        if budget > user_profile.payment_profiles[pay_method][1]:
            budget = user_profile().over_budget_check(user_profile.payment_profiles[pay_method][1], budget)
        user_profile.payment_profiles[pay_method][cat_index][1] = budget
    
    
    #return the budget value for a category profile
    def get_cat_budget(self, pay_method, cat):
        pay_method = pay_method.capitalize()
        cat = cat.capitalize()
        cat_index = user_profile().get_cat_index(pay_method, cat)
        return user_profile.payment_profiles[pay_method][cat_index][1]
    
    
    #set the notification limit for a category profile
    def change_cat_notif(self, pay_method,cat, notif_limit):
        pay_method = pay_method.capitalize()
        cat = cat.capitalize()
        cat_index = user_profile().get_cat_index(pay_method,cat)
        #checks if notif_limit value is acceptable
        #not negative and within bounds
        notif_limit = user_profile().negative_check(notif_limit)
        notif_limit = user_profile().over_budget_check(user_profile.payment_profiles[cat][1], notif_limit)
        user_profile.payment_profiles[pay_method][cat_index][2] = notif_limit
        
        
    #return the notification limit for a category profile
    def get_cat_notif(self, pay_method,cat):
        pay_method = pay_method.capitalize()
        cat = cat.capitalize()
        cat_index = user_profile().get_cat_index(pay_method,cat)
        return user_profile.payment_profiles[pay_method][cat_index][2]
    
    
    #set the amount already spent value of a category profile
    def change_cat_AAS(self, pay_method,cat,amount_spent):
        pay_method = pay_method.capitalize()
        cat = cat.capitalize()
        cat_index = user_profile().get_cat_index(pay_method,cat)
        user_profile.payment_profiles[pay_method][cat_index][3] += amount_spent
    
    
    #return the amount already spent value of a category profile
    def get_cat_AAS(self, pay_method, cat):
        pay_method = pay_method.capitalize()
        cat = cat.capitalize()
        cat_index = user_profile().get_cat_index(pay_method,cat)
        return user_profile.payment_profiles[pay_method][cat_index][3]
    
    
    #adds the amount spent on a transaction to the corresponding amount already spent value of a category
    #checks if new amount already spent value is above the notification limit for the category
    #checks if new amount already spent value isa above the budget limit for the category
    #sends notificaiton if either of the last two condictions are met
    def transaction_on_cat(self, pay_method, cat, amount_spent):
        pay_method = pay_method.capitalize()
        cat = cat.capitalize()
        #adds transaction amount to amount already spent for the category profile
        user_profile().change_cat_AAS(pay_method, cat, amount_spent)
        #gets new amount already spent value
        cat_aas = user_profile().get_cat_AAS(pay_method, cat)
        #gets notification limit for category
        cat_notif_limit = user_profile().get_cat_notif(pay_method, cat)
        #gets budget for category
        cat_budget = user_profile().get_cat_budget(pay_method, cat)
        
        if cat_aas >= cat_notif_limit:
            #send notification code here
            print("Warning, limit has been reached! Current amount spent is: {cat_aas}")
        
        if cat_aas >= cat_budget:
            #send notification code here
            print(f"Budget limit reached. Stop spending on {cat}")

    
    
    #adds the amount spent on a transaction to the corresponding amount already spent value of a payment method profile
    #checks if new amount already spent value is above the budget limit for the payment method profile
    #sends notificaiton if either of the last two condictions are met
    def transaction_on_pm(self, pay_method, amount_spent):
        pay_method = pay_method.capitalize()
        #adds transaction amount to amount already spent for the payment method
        user_profile().change_pm_aas(pay_method, amount_spent)
        #gets new amount already spent value
        pm_aas = user_profile().get_pm_aas(pay_method)
        #gets pm budget
        pm_budget = user_profile().get_pm_budget(pay_method)
        
        if pm_aas >= pm_budget:
            #send notification here
            print(f"Budget limit reached. Stop spending using {pay_method}")
    
    
    #performs transaction on both
    def transaction_both(self, pay_method, cat, amount_spent):
        user_profile().transaction_on_cat(pay_method, cat, amount_spent)
        user_profile().transaction_on_pm(pay_method, amount_spent)


#test code   
#while loop_response == 'n':
    
new_user = user_profile()
new_user.set_weekly_budget(10000)
new_user.set_weekly_notif_limit(9999)
#new_user.over_budget_check(40,50)

new_user.add_pm('credit',1635, 100)
#new_user.add_pm('debit', 8934, 200)

    
new_user.add_category('credit','food', 200, 150)

#new_user.rename_pm('credit','here')
print(new_user.payment_profiles)
#print(new_user.payment_profiles)
#new_user.change_cat_AAS('credit', 'food', 300)
#print(new_user.get_cat_AAS('credit','food'))

#print("Leave Loop?: y/n")
#loop_response = str(input())