# Importing libraries
import imaplib
import email
import yaml  #To load saved login credentials from a yaml file
import re

with open("credentials.yml") as f:
    content = f.read()
    
# from credentials.yml import user name and password
my_credentials = yaml.load(content, Loader=yaml.FullLoader)

#Load the user name and password from yaml file
user, password = my_credentials["user"], my_credentials["password"] 

#URL for IMAP connection
imap_url = 'imap.gmail.com'

# Connection with GMAIL using SSL
my_mail = imaplib.IMAP4_SSL(imap_url)

# Log in using your credentials
my_mail.login(user, password)

# Select the Inbox to fetch messages
my_mail.select('Inbox')

key = 'FROM'
value = 'amandaarreola@dusty.tamiu.edu'
_, data = my_mail.search(None, key, value)  #Search for emails with specific key and value

mail_id_list = data[0].split()  #IDs of all emails that we want to fetch 

msgs = [] # empty list to capture all messages
#Iterate through messages and extract data into the msgs list
for num in mail_id_list:
    typ, data = my_mail.fetch(num, '(RFC822)') #RFC822 returns whole message (BODY fetches just body)
    msgs.append(data) 

#Printing the Email Reciept details
for msg in msgs[::-1]:
    for response_part in msg:
        if type(response_part) is tuple:
            my_msg=email.message_from_bytes((response_part[1]))
            print("_________________________________________")
            print ("subj:", my_msg['subject'])
            print ("from:", my_msg['from'])
            print ("body:")
            for part in my_msg.walk():  
                print(part.get_content_type())
                if part.get_content_type() == 'text/plain':
                    print (part.get_payload())
                    
                    # Looka for total in the email's body paragraph by searching for the total
                    match = re.search(r"Total:\s*\$?(\d+\.\d{2})", part.get_payload())
                    if match:
                        total = match.group(1)
                        print("Total:", total)
                    else:
                        print("Total value not found.")    

#Figure out if u can use this code on regular pythone software
# **Yes you can use this code on softwares like Visual Code but extra steps must be taken**
#Needs to get the price
# **Saves the price under "total" and prints after each email iteration**
#-------------------------------
# **Can get the following information if there is a specificied structure to the email reciepts**
#Get card info if provided
#Try to categorize
