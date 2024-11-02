new_user_profile = { 'weekly_budget': 0.00, 'payment_profiles': {}}
loop_response = 'n'

#Payment Profile format:
# Method Name : [ budget, (Category Name, Budget limit, Notification limit, Amount spent)]
# amount spent will have a default of 0


#print(f"The current user profile: {new_user_profile}")

def add_pm(user_profile):
    #nameing method
    print("Enter the payment method type (string): ")
    payment_method = str(input())
    payment_method = payment_method.capitalize()
    #setting budget
    print(f"Enter the budget for {payment_method} (float):")
    pm_budget = float(input())
    #adding to profile
    user_profile['payment_profiles'][payment_method] = [pm_budget]

#pm budget setter function
def change_pm_budget(user_profile, pay_method):
    print(f"Enter new budget for: {pay_method}")
    new_budget = float(input())
    user_profile['payment_profiles'][pay_method][0] = new_budget

#pm budget getter function
def get_pm_budget(user_profile, pay_method):
    return user_profile['payment_profiles'][pay_method][0]

def add_category(user_profile, pay_method):
    #adding a category
    print("Enter the name of spending category (string): ")
    spend_cat = str(input())
    spend_cat = spend_cat.capitalize()
    #setting budget for category
    print("Enter category Budget (float): ")
    cat_budget = float(input())
    #setting notificatoin limit
    print("Enter the notificaiton limit (float):")
    notif_limit = float(input())
    #adding to profile
    user_profile['payment_profiles'][pay_method].append([spend_cat, cat_budget, notif_limit, 0])

#get index of category
def get_cat_index(user_profile, pay_method,cat):
    cat_index = 0
    
    cat_profiles = user_profile['payment_profiles'][pay_method]
    cat_profiles = cat_profiles[1:]
    
    for profile in cat_profiles:
        if profile[0] == cat:
            cat_index = cat_profiles.index(profile)
    return cat_index

#cat budget setter function
def change_cat_budget(user_profile, pay_method,cat):
    print(f"Enter new budget for {cat}: ")
    new_budget = float(input())
    cat_index = get_cat_index(user_profile, pay_method,cat)
    user_profile['payment_profiles'][pay_method][cat_index+1][1] = new_budget

#cat budget getter function
def get_cat_budget(user_profile, pay_method,cat):
    cat_index = get_cat_index(user_profile, pay_method,cat)
    return user_profile['payment_profiles'][pay_method][cat_index+1][1]

#cat notification limit setter function
def change_cat_notif(user_profile, pay_method,cat):
    print(f"Enter new notification limit for {cat}: ")
    notif_limit = float(input())
    cat_index = get_cat_index(user_profile, pay_method,cat)
    user_profile['payment_profiles'][pay_method][cat_index+1][2] = notif_limit

#cat notification limit getter function
def get_cat_notif(user_profile, pay_method,cat):
    cat_index = get_cat_index(user_profile, pay_method,cat)
    return user_profile['payment_profiles'][pay_method][cat_index+1][2]

#cat AAS setter function
def change_cat_AAS(user_profile, pay_method,cat,amount_spent):
    cat_index = get_cat_index(user_profile, pay_method,cat)
    user_profile['payment_profiles'][pay_method][cat_index+1][3] += amount_spent

#print("Enter main weekly budget: (float)")
#main_budg = float(input())
#new_user_profile['weekly_budget'] = main_budg

add_pm(new_user_profile)
    
print("Enter the payment method type to add category to(string): ")
user_pay_method = str(input())
user_pay_method = user_pay_method.capitalize()
add_category(new_user_profile,user_pay_method)
print("Enter name of category")
user_cat = str(input())
user_cat = user_cat.capitalize()

#testing loop
while loop_response == 'n':
    
    print(f'Current Profile: {new_user_profile}')
    
    change_cat_AAS(new_user_profile, user_pay_method, user_cat,100)
    
    print(f'Current Profile: {new_user_profile}')
        
    print("Leave Loop?: y/n")
    loop_response = str(input())