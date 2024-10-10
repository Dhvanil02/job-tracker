from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import threading
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json

app = Flask(__name__)

# Global dictionary to store results, keyed by some job ID
results = {}

# Helper function to add cookies
def add_cookies_to_driver(driver, cookies):
    # Add cookies to the driver
    for cookie in cookies:
        driver.add_cookie(cookie)

# Function to scrape company jobs
def scrape_company_jobs(company_name, cookies, job_id, employee_name):
    base_url = "https://www.linkedin.com/company/"
    company_url = f"{base_url}{company_name}/jobs"
    
    # Set up the Selenium WebDriver
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Open LinkedIn's main page (do this before applying cookies)
    driver.get('https://www.linkedin.com')
    
    # Wait for the page to load (you may need to change the wait condition based on what element shows up)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
    )
    
    # Add cookies to authenticate the session
    add_cookies_to_driver(driver, cookies)
    
    # Reload the page after adding cookies to apply them correctly
    # driver.get('https://www.linkedin.com')
    driver.refresh()
    
    # Now navigate directly to the company jobs page without refreshing in between
    print(f'''{company_url=}''')
    driver.get(company_url)
    # Wait for the job listings to load (wait for specific elements)
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="job-card-square__main"]'))
        )

        # Scrape job listings once the element is found
        jobs = driver.find_element(By.CSS_SELECTOR, '[class="org-jobs-recently-posted-jobs-module__show-all-jobs-btn"] a')
        driver.get(jobs.get_property('href'))
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[class="scaffold-layout__list-container"]'))
        )
        jobs = driver.find_elements(By.CSS_SELECTOR, '[class="scaffold-layout__list-container"] li[class*="jobs-search-results__list-item occludable-update"]')

        python_jobs = []
        for job in jobs:
            try:
                job_title = job.find_element(By.CSS_SELECTOR, '[class*="job-card-list__title"] [aria-hidden="true"]')
                print(job_title.text)

                if 'Python Developer' in job_title.text:
                    job_info = {
                        'title': job_title.text,
                        'company_name': job.find_element(By.CSS_SELECTOR, '[class="job-card-container__primary-description "]').text,
                        'location': job.find_element(By.CSS_SELECTOR, '[class="job-card-container__metadata-item "]').text,
                        'url': job.find_element(By.CSS_SELECTOR, '[class*="job-card-list__title"]').get_attribute('href')
                    }
                    python_jobs.append(job_info)
            except Exception as e:
                print(f"Error occurred: {e}")
                continue
        
        results[job_id] = python_jobs
        if len(python_jobs) > 0:
            send_email("dhvanil02@gmail.com",python_jobs, employee_name)
    except Exception as e:
        print(f"Error occurred: {e}")
        return []
    finally:
        driver.quit()

# API endpoint for scraping jobs
@app.route('/scrape-jobs', methods=['POST'])
def scrape_jobs():
    try:
        data = request.get_json()
        li_at = data.get('li_at')
        jsessionid = data.get('JSESSIONID')
        company_id = data.get('companyUrl')
        employee_name = data.get('employeeName')
        print(f'''{company_id=}''')
        
        if not li_at or not jsessionid:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Prepare cookies
        cookies = [
            {'name': 'li_at', 'value': li_at},
            {'name': 'JSESSIONID', 'value': jsessionid}
        ]

        # Generate a job ID to track the request
        job_id = str(time.time())
        threading.Thread(target=scrape_company_jobs, args=(company_id, cookies, job_id, employee_name)).start()
        
        return jsonify({"message": "Job processing", "job_id": job_id}), 202
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# def send_mail_user(python_jobs, user_name):
#     fromaddr = "dhvanil.magictech@gmail.com"
#     toaddr = "dhvanil02@gmail.com"
#     msg = MIMEMultipart('alternative')
#     msg['From'] = fromaddr
#     msg['To'] = toaddr
#     msg['Subject'] = subject

#     subject = "Follow-up on Flutter App Assistance"
#     body = f"""\
#     Hello {user_name},

#     Hope you are doing fine.

#     We are in a discussion on LinkedIn where you mentioned you needed some assistance with your app written in Flutter. You asked about the rates to which we shared part-time rates of USD xy and full-time rates of USD xy per hour. Since I didn’t hear back from you, I thought of dropping you an email.

#     Looking forward to hearing from you soon; we can also schedule a quick call to explore how we can assist you with your needs!
#     """
#     # body_html = render_to_string("payment-failed-email.html", context={'username': username})
#     # body_text = strip_tags(body_html)
#     # msg.content_subtype = "html" 
#     msg.attach(MIMEText(body_text, 'plain'))
#     msg.attach(MIMEText(body_html, 'html'))
#     try:
#         smtp_server = "smtp.gmail.com"
#         smtp_port = "587"
#         # server = smtplib.SMTP('smtp.gmail.com:587')
#         server = smtplib.SMTP(f'{smtp_server}:{smtp_port}')
#         server.starttls()
#         server.login(fromaddr, str("ojiv ekhr uvsn dgcr"))
#         text = msg.as_string()
#         server.sendmail(fromaddr, toaddr, text)
#         print('Email sent successfully')
#     except Exception as e:
#         print(f'Error sending email: {str(e)}')
#     finally:
#         server.quit()


def send_email(to_email, json_data, user_name):
    # Email and password for the sender's email account
    from_email = "dhvanil.magictech@gmail.com"
    password = "ojiv ekhr uvsn dgcr"  # Use an app password if 2FA is enabled
    json_dumps_data = json.dumps(json_data, indent=4)
    # Set up the MIME
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = "Available Python Job Opportunities"

    body = f"""\
        Hello {user_name},

        Hope you are doing well.

        I wanted to share some exciting Python job opportunities we currently have available. Below is the detailed information in JSON format:

        {json_dumps_data}

        Please let me know if you're interested in any of these positions, and we can schedule a quick call to discuss further!

        Looking forward to hearing from you soon.

        Best regards,
        Job Tracker
    """
    # Attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # Create a secure SSL context and send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()  # Upgrade the connection to secure
        server.login(from_email, password)  # Log in to the server
        server.send_message(msg)  # Send the email
# Run the app
if __name__ == '__main__':
    app.run(debug=True)
