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
