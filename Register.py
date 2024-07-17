import time
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import SMS
import os

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

def login():
    driver.get('https://sso.uga.edu/cas/login?TARGET=https%3A%2F%2Fathena-prod.uga.edu%2FStudentSelfService%2Flogin%2Fcas')
    username = driver.find_element(By.ID, 'username')
    password = driver.find_element(By.ID, 'password')
    username.send_keys(os.environ.get('userID'))
    password.send_keys(os.environ.get('password'))
    driver.find_element('name', 'submit').click()
    SMS.send(os.environ.get('phone'), 'tmobile', wait.until(EC.presence_of_element_located((By.CLASS_NAME, "verification-code"))).text)
    WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "dont-trust-browser-button"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "//label[text()='Student & Registration']"))).click()
    driver.find_element(By.XPATH, '//a[@href="https://sso.uga.edu/cas/login?TARGET=https%3A%2F%2Fathena-prod.uga.edu%2FStudentRegistrationSsb%2Flogin%2Fcas"]').click()
    driver.switch_to.window(driver.window_handles[-1])
    wait.until(EC.element_to_be_clickable((By.ID, "registerLink"))).click()


def selectTerm():
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "s2id_txt_term")))
    dropdown.click()
    wait.until(EC.element_to_be_clickable((By.ID, "202408"))).click()
    driver.find_element(By.ID, 'term-go').click()


def findCourse(crn):
    keyword = wait.until(EC.element_to_be_clickable((By.ID, "txt_keywordlike")))
    keyword.send_keys(crn)
    keyword.send_keys(Keys.RETURN)

def checkCourseAvailability(crn):
    driver.get('https://athena-prod.uga.edu/StudentRegistrationSsb/ssb/term/termSelection?mode=registration')
    wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@class='title' and text()='Browse Classes']"))).click()
    selectTerm()
    findCourse(crn)
    row = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#searchResultsTable tr[data-id]")))
    status = row.find_element(By.XPATH, './/td[@data-property="status"]').text
    while 'FULL' in status.upper():
        time.sleep(10)
        wait.until(EC.element_to_be_clickable((By.ID, 'search-again-button'))).click()
        driver.find_element(By.ID, 'search-go').click()
        row = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#searchResultsTable tr[data-id]")))
        status = row.find_element(By.XPATH, './/td[@data-property="status"]').text
    return True


def register(crn):
    row = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#searchResultsTable tr[data-id]")))
    row.find_element(By.ID, f'addSection202408{crn}').click()
    wait.until(EC.element_to_be_clickable((By.ID, 'saveButton'))).click()
    time.sleep(10)


def unregister(crn):
    rows = wait.until(EC.presence_of_all_elements_located((
            By.CSS_SELECTOR, ".ui-layout-east.ui-widget-content.mySchedule.mySchedule-summary tr[data-id]")))
    for row in rows:
        courseCrn = row.find_element(By.XPATH, './/td[@data-property="courseReferenceNumber"]').text
        if courseCrn == str(crn):
            row.find_element(By.XPATH, f'.//div[@id="s2id_action-{crn}-ddl"]').click()
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(driver)
            actions.send_keys(Keys.ARROW_DOWN)
            actions.send_keys(Keys.ENTER)
            actions.perform()
            break



if(checkCourseAvailability(44457)):
    login()
    selectTerm()
    findCourse(44457)
    unregister(59894)
    register()