from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()


def login():
    driver.get('https://sso.uga.edu/cas/login?TARGET=https%3A%2F%2Fathena-prod.uga.edu%2FStudentSelfService%2Flogin%2Fcas')
    username = driver.find_element(By.ID, 'username')
    password = driver.find_element(By.ID, 'password')
    username.send_keys('dko48341')
    password.send_keys('Dd20040929+@')
    driver.find_element('name', 'submit').click()


def selectTerm():
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "toggle_1"))).click()
    driver.find_element(By.XPATH, '//a[@href="https://sso.uga.edu/cas/login?TARGET=https%3A%2F%2Fathena-prod.uga.edu%2FStudentRegistrationSsb%2Flogin%2Fcas"]').click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "registerLink"))).click()
    driver.get('https://athena-prod.uga.edu/StudentRegistrationSsb/ssb/term/termSelection?mode=registration')
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "txt_term")))
    dropdown.click()
    dropdown.send_keys("Fall 2024")
    dropdown.send_keys(Keys.RETURN)
    driver.find_element(By.ID, 'term-go').click()


def findCourse(S, C):
    subject = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "s2id_autogen8")))
    subject.click()
    subject.send_keys(S)
    subject.send_keys(Keys.RETURN)
    courseNumber = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "txt_courseNumber")))
    courseNumber.click()
    courseNumber.send_keys(C)
    courseNumber.send_keys(Keys.RETURN)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "search-go"))).click()


def checkCourseAvailability(crn):
    rows = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#searchResultsTable tr[data-id]")))
    for row in rows:
        courseCRN = row.find_element(By.XPATH, './/td[@data-property="courseReferenceNumber"]').text
        if courseCRN == str(crn):
            detailsLink = row.find_element(By.CSS_SELECTOR, ".section-details-link")
            detailsLink.click()

            # Wait for the details to load and check the enrollment seats available
            enrollmentSeats = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//span[contains(text(), 'Enrollment Seats Available:')]/following-sibling::span"))
            ).text

            # Convert the text to an integer to check if seats are available
            seatsAvailable = int(enrollmentSeats)
            result = seatsAvailable > 0

            # Close the popup
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".ui-icon.ui-icon-closethick"))).click()

            return result
    return False


def register(crn):
    rows = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#searchResultsTable tr[data-id]")))
    for row in rows:
        courseCrn = row.find_element(By.XPATH, './/td[@data-property="courseReferenceNumber"]').text
        if courseCrn == str(crn):
            row.find_element(By.ID, f'addSection202408{crn}').click()

            # Click the submit button to register
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'saveButton'))).click()


def unregister(crn):
    rows = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((
            By.CSS_SELECTOR, ".ui-layout-east.ui-widget-content.mySchedule.mySchedule-summary tr[data-id]")))
    for row in rows:
        courseCrn = row.find_element(By.XPATH, './/td[@data-property="courseReferenceNumber"]').text
        if courseCrn == str(crn):
            row.find_element(By.ID, f'action-{crn}-ddl').click()

            # Select "Web Drop" from the dropdown
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//li[@role='option']//div[text()='Web Drop']"))
            ).click()
            return True
    return False


login()
selectTerm()
''' findCourse('CSCI', '4300')
if checkCourseAvailability(44457):
    unregister(59894)
    register(44457)
elif checkCourseAvailability(31786):
    unregister(59894)
    register(31786)
else:
    print("No seats available")'''