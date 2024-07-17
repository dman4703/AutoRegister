import time
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import SMS
import os

# Initialize the Chrome WebDriver
driver = webdriver.Chrome()
# Create an explicit wait with a timeout of 10 seconds
wait = WebDriverWait(driver, 10)

def login():
    # navigate to uga login page
    driver.get('https://sso.uga.edu/cas/login?TARGET=https%3A%2F%2Fathena-prod.uga.edu%2FStudentSelfService%2Flogin%2Fcas')
    # populate username and password
    username = driver.find_element(By.ID, 'username')
    password = driver.find_element(By.ID, 'password')
    username.send_keys(os.environ.get('userID'))
    password.send_keys(os.environ.get('password'))
    # submit credentials
    driver.find_element('name', 'submit').click()
    # send 2FA verificaiton to phone
    SMS.send(os.environ.get('phone'), 'tmobile', wait.until(EC.presence_of_element_located((By.CLASS_NAME, "verification-code"))).text, 'DUO')
    WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "dont-trust-browser-button"))).click()
    # navigate through to registration page
    wait.until(EC.element_to_be_clickable((By.XPATH, "//label[text()='Student & Registration']"))).click()
    driver.find_element(By.XPATH, '//a[@href="https://sso.uga.edu/cas/login?TARGET=https%3A%2F%2Fathena-prod.uga.edu%2FStudentRegistrationSsb%2Flogin%2Fcas"]').click()
    # switch to newly opened window
    driver.switch_to.window(driver.window_handles[-1])
    wait.until(EC.element_to_be_clickable((By.ID, "registerLink"))).click()


def selectTerm():
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "s2id_txt_term")))
    dropdown.click()
    # select 'Fall 2024'
    wait.until(EC.element_to_be_clickable((By.ID, "202408"))).click()
    driver.find_element(By.ID, 'term-go').click()


def findCourse(crn):
    # use the class specific crn to locate the exact class
    keyword = wait.until(EC.element_to_be_clickable((By.ID, "txt_keywordlike")))
    keyword.clear()
    keyword.send_keys(crn)
    keyword.send_keys(Keys.RETURN)


def checkCourseAvailability(*crns):
    # navigate to public server
    driver.get('https://athena-prod.uga.edu/StudentRegistrationSsb/ssb/term/termSelection?mode=registration')
    wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@class='title' and text()='Browse Classes']"))).click()
    selectTerm()
    # check for open seats every 60 seconds
    status = 'FULL'
    while 'FULL' in status.upper():
        for crn in crns:
            findCourse(crn)
            time.sleep(10)
            # locate the row the class is populated in
            row = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#searchResultsTable tr[data-id]")))
            # get the class status
            status = row.find_element(By.XPATH, './/td[@data-property="status"]').text
            if 'FULL' not in status.upper():
                # send a text message when an open seat is found
                SMS.send(os.environ.get('phone'), 'tmobile', 'OPEN SEAT FOUND for {}'.format(crn), 'OPEN SEAT FOUND for {}'.format(crn))
                print('OPEN SEAT FOUND for {}'.format(crn))
                return crn
            print('{} is {}'.format(crn, status))
            wait.until(EC.element_to_be_clickable((By.ID, 'search-again-button'))).click()
    return None


def register(crn):
    # add and submit the class
    row = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#searchResultsTable tr[data-id]")))
    row.find_element(By.ID, f'addSection202408{crn}').click()
    wait.until(EC.element_to_be_clickable((By.ID, 'saveButton'))).click()
    SMS.send(os.environ.get('phone'), 'tmobile', 'CLASS REGISTERED', 'CLASS REGISTERED')
    time.sleep(10)


def unregister(crn):
    # find the currently registered class in the list of registered classes
    rows = wait.until(EC.presence_of_all_elements_located((
            By.CSS_SELECTOR, ".ui-layout-east.ui-widget-content.mySchedule.mySchedule-summary tr[data-id]")))
    for row in rows:
        courseCrn = row.find_element(By.XPATH, './/td[@data-property="courseReferenceNumber"]').text
        if courseCrn == str(crn):
            # unregister it
            row.find_element(By.XPATH, f'.//div[@id="s2id_action-{crn}-ddl"]').click()
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(driver)
            actions.send_keys(Keys.ARROW_DOWN)
            actions.send_keys(Keys.ENTER)
            actions.perform()
            break
    # notify of unregistration
    SMS.send(os.environ.get('phone'), 'tmobile','CURRENT CLASS UNREGISTERED', 'CURRENT CLASS UNREGISTERED')


try:
    openCrn = checkCourseAvailability('44457')

    if openCrn is not None:
        login()
        selectTerm()
        findCourse(openCrn)
        unregister('59894')
        register(openCrn)
except Exception as e:
    # Send an SMS with the error details
    message = 'An exception occurred: {}'.format(e)
    SMS.send(os.environ.get('phone'), 'tmobile', 'AUTO REGISTER ERROR', message)
    print(message)
finally:
    # Close the browser
    driver.quit()