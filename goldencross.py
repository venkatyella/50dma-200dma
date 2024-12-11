from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time 
import smtplib 
from email.mime.text import MIMEText 
from email.mime.multipart import MIMEMultipart
import datetime
import nifpy
from nsepy import get_history

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# Set up Selenium WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)


def is_recent_data(date_str, days=60):
    date = datetime.datetime.strptime(date_str,"%Y-%m-%d")
    return (datetime.datetime.now() - date).days <= days

def store_update_file(data,data_to_mail):
    existing_data = {}
    
    try:
        with open('goldencross.txt', 'r') as file:
            for line in file:
                string, date_str = line.strip().split('\t')
                existing_data[string]=date_str
    except FileNotFoundError:
        pass

    current_date = datetime.datetime.now()
    filtered_data = {string : date_str for string, date_str in existing_data.items() if (current_date - datetime.datetime.strptime(date_str, "%Y-%m-%d")).days <= 90}

 #   filtered_data = { string: (date_str, closing) for string, date_str, closing in existing_data if (current_date - datetime.datetime.strptime(date_str, "%Y-%m-%d")).days <= 90 }

    with open('goldencross.txt', 'w') as file:
        for string, date_str in filtered_data.items():
            file.write(f"{string}\t{date_str}\n")

        for string in data:
            if string in filtered_data:
                if is_recent_data(filtered_data[string], 60):
                    continue
            current_date_str = current_date.strftime("%Y-%m-%d")
            if string != 'Candle-Stick Point and Figure Fundamentals':
                stock_data = get_history(symbol=string, start=current_date - datetime.timedelta(days=100), end=current_date) 
                print(stock_data)
                closing_price = stock_data['Open'].values[0] if not stock_data.empty else None
                data_to_mail.append(f"{string}\t{current_date_str}\n")
                file.write(f"{string}\t{current_date_str}\n")
          #  filtered_data[string] = current_date_str
        #data = data_to_mail

try:
    # Open the screener URL
    driver.get("https://chartink.com/screener/50dma-200dma-5")

    # Wait for the page to load
    time.sleep(1)  # Use explicit delay

    # Parse the page source
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Extract stock data (update the selectors based on page structure)
    stocks = []
    data= []
    for row in soup.select("table tbody tr"):  # Example selector
        cells = row.find_all("td") 
        if len(cells) > 2:
	        symbol = cells[2].text.strip()
	        stocks.append(symbol)
    store_update_file(stocks,data)

finally:
    # Close the driver
    driver.quit()


# Email configuration
email_sender = 'firstclaps@gmail.com'
email_password = 'ajyq xkpm ugfd fspl'
email_recipient = 'firstclaps@gmail.com'
email_subject = 'golden cross'

html_body = """ <html> 
                <body> 
                <h2>Stock Symbols and Dates</h2> 
                <table border="1">
                 <tr> 
                 <th> Stock </th> 
                 <th> Date </th> 
                 </tr>
             """ 
for item in data: 
    l = item.split("\t")
    html_body += f""" 
       <tr> 
       <td> {l[0]} </td> 
       <td> {l[1]} </td>
       </tr> 
       """ 
html_body += """ </table> </body> </html> """

# Create email content
#email_body = ''.join(data)
msg = MIMEMultipart()
msg['From'] = email_sender
msg['To'] = email_recipient
msg['Subject'] = email_subject
msg.attach(MIMEText(html_body, 'html'))

# Send the email
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_sender, email_password)
    server.sendmail(email_sender, email_recipient, msg.as_string())
    server.quit()
    print('Email sent successfully!')
except Exception as e:
    print(f'Failed to send email: {e}')

