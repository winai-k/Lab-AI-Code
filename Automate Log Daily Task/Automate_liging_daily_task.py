import pyautogui
import time
import os
import openpyxl
import psutil  # To check running processes
import subprocess  # To execute taskkill command
import tkinter as tk  # For progress display popup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from tqdm import tqdm  # For progress display
import logging  # For logging execution status
import sys  # To force program exit

# Set delays to make UI interaction stable
pyautogui.PAUSE = 1

# Configure logging
log_file = os.path.join(os.path.dirname(__file__), "execution_log.txt")
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def launch_excel(file_path):
    """Opens an Excel file."""
    logging.info(f"Function: launch_excel > Started.")

    os.startfile(file_path)
    time.sleep(5)  # Wait for Excel to open
    logging.info(f"Function: launch_excel > Launch excel file completed.")

def read_excel(file_path, sheet_name):
    """Reads data from the specified Excel sheet and returns only the displayed values as a matrix."""
    logging.info(f"Function: read_excel > Started.")

    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet = wb[sheet_name]
    matrix = [[cell.value for cell in row] for row in sheet.iter_rows()]
    logging.info(f"Function: read_excel > Read excel data successfully.")

    wb.close()  # Close the workbook after reading
    close_excel()  # Ensure Excel is closed after reading
    logging.info(f"Function: read_excel > Close excel file completed.")

    return matrix

def assign_variables(matrix):
    """Assigns variables based on matrix values."""
    logging.info(f"Function: assign_variables > Started.")

    headers = ["UID", "P_Site", "P_Type", "P_ID", "P_Code", "P_Location", "Subject_Action", "Activity_Summary", "Taxi_Expense", "Taxi_Go_Back", "Taxi_Trollwey", "P_Bub_item", "Taxi_Remark", "Staff", "T_Arrived", "T_Started", "T_Finished", "T_Departed"]
    for index, header in enumerate(headers):
        if index < len(matrix):  # Ensure the column exists
            globals()[header] = matrix[index]
            print(f"Variable {header} to {matrix[index]}")  # Debugging output
            logging.info(f"Function: assign_variables > Variable {header} to {matrix[index]}.")

    logging.info(f"Function: assign_variables > Assign Variables completed.")

def close_excel():
    """Closes all instances of Microsoft Excel."""
    logging.info(f"Function: close_excel > Started.")

    for process in psutil.process_iter():
        try:
            if "EXCEL.EXE" in process.name():
                process.terminate()  # Kill the process
                print("Closed Excel successfully.")
                logging.info(f"Function: close_excel > Close excel file successfully.")

        except psutil.NoSuchProcess:
            pass

def get_login_credentials(file_path):
    """Reads username and password from a text file."""
    logging.info(f"Function: get_login_credentials > Started.")

    try:
        with open(file_path, "r") as file:
            logging.info(f"Function: get_login_credentials > Open file successfully.")

            lines = file.readlines()
            if len(lines) >= 2:
                username = lines[0].strip()
                password = lines[1].strip()
                logging.info(f"Function: get_login_credentials > Get username password completed.")

                return username, password
            else:
                logging.error(f"Function: get_login_credentials > File format incorrect. Expected username and password on separate lines.")
                raise ValueError("File format incorrect. Expected username and password on separate lines.")
            
    except FileNotFoundError:
        logging.error(f"Function: get_login_credentials > Login credentials file not found: {file_path}.")
        raise FileNotFoundError(f"Login credentials file not found: {file_path}")

def login_web(username, password, url):
    """Logs into a web application using Selenium and waits for the page to load completely."""
    logging.info(f"Function: login_web > Started.")

    options = webdriver.ChromeOptions()
    options.add_argument("--force-device-scale-factor=0.65")  # Adjust browser zoom
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    logging.info(f"Function: login_web > Open web browser successfully.")
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(username)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(password)
    logging.info(f"Function: login_web > Send username password successfully.")

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btn-login"))).click()
    
    # Wait for page to load completely
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "button")))
    logging.info(f"Function: login_web > Login Web CSM completed.")
    return driver

def create_new_sar(driver):
    """Create the NEW SAR button and selects 'สร้างและบันทึกแล้วเสร็จ'."""
    logging.info(f"Function: create_new_sar > Started.")

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'NEW SAR')]"))).click()
    logging.info(f"Function: create_new_sar > Click (NEW SAR) successfully.")

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@data-menu='menu-create-activity-onprocess']"))).click()
    logging.info(f"Function: create_new_sar > Click (สร้างและบันทึกแล้วเสร็จ) successfully.")

    # Wait for page to load completely
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "button")))
    logging.info(f"Function: create_new_sar > Create the NEW SAR completed.")

def module_ma_warranty(driver):
    """Navigates to MA/Warranty module on P_Site selection."""
    logging.info("Function: module_ma_warranty > Started.")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "process_act_module_2"))).click()
    logging.info("Function: module_ma_warranty > Click (MA/Warranty) successfully.")

    p_id = globals().get("P_ID", "")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//*[@id='item_{p_id}']"))).click()
    logging.info(f"Function: module_ma_warranty > Clicked item_{p_id} successfully.")

    """Fills Field Task & Sub Task & Onsite Location & Action & Staff & Date Time & Activity Summary."""
    iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div#page iframe")))
    driver.switch_to.frame(iframe)
    logging.info("Function: module_ma_warranty > Switched to iframe successfully.")

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='select2-site_location-container']"))).click()
    driver.find_element(By.XPATH, "//*[@id='createNewActivity']/span/span/span[1]/input").send_keys(globals().get("P_Location", ""))
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='select2-site_location-results']/li[1]"))).click()
    logging.info("Function: module_ma_warranty > Filled site location successfully.")
    
    driver.find_element(By.ID, "task_note").send_keys(globals().get("Subject_Action", ""))
    logging.info("Function: module_ma_warranty > Filled Subject Action successfully.")

    # Assign date/time fields
    driver.find_element(By.ID, "ArrivalDate").send_keys(globals().get("T_Started", ""))     # Assign field "ArrivalDate"
    driver.find_element(By.ID, "StartDate").click()                                         # Assign field "StartDate"
    driver.find_element(By.ID, "FinishDate").click()
    driver.find_element(By.ID, "FinishDate").send_keys(globals().get("T_Finished", ""))     # Assign field "FinishDate"
    driver.find_element(By.ID, "DepartDate").click()
    driver.find_element(By.ID, "DepartDate").send_keys(globals().get("T_Departed", ""))     # Assign field "DepartDate"
    logging.info("Function: module_ma_warranty > Filled date fields successfully.")
    
    driver.find_element(By.ID, "finish_text").click()
    driver.find_element(By.ID, "finish_text").send_keys(globals().get("Activity_Summary", ""))
    logging.info("Function: module_ma_warranty > Filled Activity Summary successfully.")

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "showSubmitWorkOrderButtonDD"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "SubmitButtonWorkOrderd"))).click()
    logging.info("Function: module_ma_warranty > Submitted Work Order successfully.")
    
    time.sleep(5)
    driver.switch_to.default_content()
    iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div#page iframe")))
    driver.switch_to.frame(iframe)
    logging.info("Function: module_ma_warranty > Switched back to iframe successfully.")

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "showSubmitCloseWorkOrderButton"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "SubmitButtonCloseWorkOrder"))).click()
    logging.info("Function: module_ma_warranty > Submitted Close Work Order successfully.")

    module_record_expenses(driver)

    """Back To Home Page."""
    driver.switch_to.default_content()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='footer-bar']/a[1]"))).click()
    logging.info("Function: module_ma_warranty > Navigated back to Home Page successfully.")

def module_record_expenses(driver):
    logging.info("Function: module_record_expenses > Started.")

    # Wait for page to load completely
    time.sleep(4)
    driver.switch_to.default_content()
    iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div#page iframe")))
    driver.switch_to.frame(iframe)
    logging.info("Function: module_record_expenses > Switched to iframe successfully.")

    if globals().get("Taxi_Expense") == True:
        logging.info("Function: module_record_expenses > Taxi_Expense is True.")
        
        correct_radio_xpath = "/html/body/div[1]/div[1]/div/div/div[1]/div/form[1]/div[4]/div[5]/div/div[1]/div/div/div[1]/input"
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, correct_radio_xpath))).click()
        logging.info("Function: module_record_expenses > Clicked Taxi Expense radio button successfully.")

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='taxi_expense']/div[2]/span/span[1]/span"))).click()
        location_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/span/span/span[1]/input")))
        location_field.send_keys(globals().get("P_Location", ""))
        time.sleep(1)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='select2-site_location-results']/li[1]"))).click()
        logging.info("Function: module_record_expenses > Filled site location successfully.")

        if globals().get("Taxi_Go_Back") == True:
            logging.info("Function: module_record_expenses > Taxi_Go_Back is True.")
            #print(f"Taxi_Go_Back == True")  # Debugging output
            driver.find_element(By.XPATH, "//*[@id='taxi_triptype']/option[2]").click()
            logging.info("Function: module_record_expenses > Selected Taxi Go-Back option successfully.")

        if globals().get("Taxi_Trollwey") != None:
            taxi_trollwey_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "trollway_cost")))
            taxi_trollwey_field.send_keys(Keys.BACK_SPACE)
            taxi_trollwey_field.send_keys(globals().get("Taxi_Trollwey", ""))
            logging.info("Function: module_record_expenses > Filled Taxi Trollwey cost successfully.")

        if globals().get("Taxi_Trollwey") != None:
            driver.find_element(By.ID, "taxi_remark").send_keys(globals().get("Taxi_Remark", ""))
            logging.info("Function: module_record_expenses > Filled Taxi Remark successfully.")

        bub_item_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "bubitem")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", bub_item_field)
        time.sleep(2)
        bub_item_field.click()
        logging.info("Function: module_record_expenses > Clicked Bub Item dropdown successfully.")
        
        p_bub_item = globals().get("P_Bub_item", "")
        bub_item_xpath = f"//select[@id='bubitem']/option[contains(normalize-space(),'{p_bub_item}')]"
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, bub_item_xpath))).click()
        bub_item_field.click()
        logging.info(f"Function: module_record_expenses > Selected Bub Item: {p_bub_item} successfully.")

    elif globals().get("Taxi_Expense") == False:
        logging.info("Function: module_record_expenses > Taxi_Expense is False.")
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "inlineRadio3"))).click()
        logging.info("Function: module_record_expenses > Clicked No Expense radio button successfully.")

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "showSubmitWorkOrderButtonDD"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "SubmitButtonWorkOrderd"))).click()
    logging.info("Function: module_record_expenses > Submitted Taxi Expense Work Order successfully.")

    logging.info("Function: module_record_expenses > Completed.")

def module_record_expenses_continue(driver):
    """Go To SAR."""
    # Click the confirm button "SAR รอดำเนินการ"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "total_act"))).click()

    # Select the option "Adhoc-1"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='tab-1']/div[1]/a"))).click()
    time.sleep(3)
    # Switch to the correct iframe before interacting with form elements
    iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div#page iframe")))
    driver.switch_to.frame(iframe)

    if globals().get("Taxi_Expense") == True:
        # Click the radio button "inlineRadio1"
        correct_radio_xpath = "/html/body/div[1]/div[1]/div/div/div[1]/div/form[1]/div[4]/div[5]/div/div[1]/div/div/div[1]/input"
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, correct_radio_xpath))).click()

        # Type Onsite location
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='taxi_expense']/div[2]/span/span[1]/span"))).click()
        location_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/span/span/span[1]/input")))
        location_field.send_keys(globals().get("P_Location", ""))
        time.sleep(1)

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='select2-site_location-results']/li[1]"))).click()

        if globals().get("Taxi_Go_Back") == True:
            print(f"Taxi_Go_Back == True")  # Debugging output
            # Select the option "Yes" in case ไป-กลับ
            driver.find_element(By.XPATH, "//*[@id='taxi_triptype']/option[2]").click()

        # Assign Taxi_Trollwey on text field "trollway_cost"
        if globals().get("Taxi_Trollwey") != None:
            taxi_trollwey_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "trollway_cost")))
            taxi_trollwey_field.send_keys(Keys.BACK_SPACE)
            taxi_trollwey_field.send_keys(globals().get("Taxi_Trollwey", ""))

        # Assign Taxi_Remark on text field "taxi_remark"
        if globals().get("Taxi_Trollwey") != None:
            driver.find_element(By.ID, "taxi_remark").send_keys(globals().get("Taxi_Remark", ""))

        # ScrollIntoView and Click select "bubitem"
        bub_item_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "bubitem")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", bub_item_field)
        time.sleep(2)
        bub_item_field.click()
        
        # Select specific menu item based on P_Bub_item
        p_bub_item = globals().get("P_Bub_item", "")
        bub_item_xpath = f"//select[@id='bubitem']/option[contains(normalize-space(),'{p_bub_item}')]"
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, bub_item_xpath))).click()
        bub_item_field.click()

    elif globals().get("Taxi_Expense") == False:
        # Click select radio "inlineRadio3" in case ไม่มีค่าเดินทาง
        #radio_no_expense = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "inlineRadio3")))
        #driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", radio_no_expense)
        #time.sleep(3)
        #radio_no_expense.click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "inlineRadio3"))).click()


    # Click set checked check box in "ส่งข้อมูล"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "showSubmitWorkOrderButtonDD"))).click()
    # Click the confirm button "ยืนยัน"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "SubmitButtonWorkOrderd"))).click()

    """Back To Home Page."""
    # Switch back to the main content after interacting with the iframe
    driver.switch_to.default_content()
    # Click the confirm button "ใบงานที่เกี่ยวข้อง"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='footer-bar']/a[1]"))).click()

def module_adhoc(driver):
    """Navigates to Adhoc module based on P_Site selection."""
    logging.info("Function: module_adhoc > Started.")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "process_act_module_5"))).click()
    logging.info("Function: module_adhoc > Clicked Adhoc module successfully.")
    
    p_site = globals().get("P_Site", "")
    menu_xpath = f"//h1[contains(text(),'{p_site}')]"
    select_site_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, menu_xpath)))
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", select_site_field)
    time.sleep(2)
    select_site_field.click()
    logging.info(f"Function: module_adhoc > Clicked site: {p_site} successfully.")
    
    """Fills Field Task & Sub Task & Action & Staff & Assign Date Time."""
    iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div#page iframe")))
    driver.switch_to.frame(iframe)
    logging.info("Function: module_adhoc > Switched to iframe successfully.")
    
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "task_act"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//option[text()='Adhoc']"))).click()
    logging.info("Function: module_adhoc > Selected Adhoc task successfully.")

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "flexCheckChecked_0"))).click()
    logging.info("Function: module_adhoc > Checked Sub Task: Adhoc successfully.")

    driver.find_element(By.ID, "task_note").send_keys(globals().get("Subject_Action", ""))
    logging.info("Function: module_adhoc > Filled Subject Action successfully.")

    staff_input = driver.find_element(By.XPATH, "//*[@id='createNewActivityForm']/div[9]/span/span[1]/span/span/textarea")
    staff_input.click()
    staff_input.send_keys(globals().get("Staff", ""))
    staff_input.send_keys(Keys.ENTER)
    logging.info("Function: module_adhoc > Selected Staff successfully.")

    driver.find_element(By.ID, "AssignDate").send_keys(globals().get("T_Started", ""))      # Assign field "StartDate"
    driver.find_element(By.XPATH, "//*[@id='AssignDate']").click()
    logging.info("Function: module_adhoc > Filled Assigned Date successfully.")

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "showSubmitWorkOrderButton"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "SubmitButtonWorkOrder"))).click()
    logging.info("Function: module_adhoc > Submitted Work Order successfully.")

    # Wait for page to load completely
    time.sleep(5)
    driver.switch_to.default_content()
    iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div#page iframe")))
    driver.switch_to.frame(iframe)
    logging.info("Function: module_adhoc > Switched to iframe successfully.")

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btn_start_act"))).click()
    logging.info("Function: module_adhoc > Checked Starte Activity successfully.")

    """Fills Field Arrived & Start Time."""
    # Click select radio "isArriveAndStart"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "inlineRadio2"))).click()
    driver.find_element(By.ID, "ArrivalDate").send_keys(globals().get("T_Started", ""))     # Assign field "ArrivalDate"
    driver.find_element(By.XPATH, "//*[@id='ArrivalDate']").click()
    logging.info("Function: module_adhoc > Filled Arrival and Start Date successfully.")
    
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "showSubmitWorkOrderButton"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "SubmitButtonWorkOrder"))).click()
    logging.info("Function: module_adhoc > Confirmed Arrival and Start successfully.")

    """Fills Field Finished & Depart Time and Activity Summary."""
    # Click select radio "isFinishedAndDepart2"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "isFinishedAndDepart2"))).click()
    driver.find_element(By.ID, "FinishDate").send_keys(globals().get("T_Finished", ""))     # Assign field "FinishDate"
    driver.find_element(By.XPATH, "//*[@id='FinishDate']").click()
    logging.info("Function: module_adhoc > Filled Finish and Depart Date successfully.")
    
    driver.find_element(By.ID, "finish_text").send_keys(globals().get("Activity_Summary", ""))
    logging.info("Function: module_adhoc > Filled Activity Summary successfully.")

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "showSubmitWorkOrderButton"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "SubmitButtonWorkOrder"))).click()
    logging.info("Function: module_adhoc > Submitted Finished Work Order successfully.")

    """Check Summary Detail."""
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "showSubmitCloseWorkOrderButton"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "SubmitButtonCloseWorkOrder"))).click()
    logging.info("Function: module_adhoc > Submitted Close Work Order successfully.")

    """Check Taxi Expense Detail."""
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "showSubmitWorkOrderButton"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "SubmitButtonWorkOrder"))).click()
    logging.info("Function: module_adhoc > Submitted Taxi Expense Work Order successfully.")

    """Back To Home Page."""
    driver.switch_to.default_content()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='footer-bar']/a[1]"))).click()
    logging.info("Function: module_adhoc > Navigated back to Home Page successfully.")

    logging.info("Function: module_adhoc > Completed.")

def module_adhoc_continue(driver):
    """Go To SAR."""
    # Click the confirm button "SAR รอดำเนินการ"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "total_act"))).click()

    # Select the option "Adhoc-1"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='tab-1']/div[1]/a"))).click()
    time.sleep(5)
    # Switch to the correct iframe before interacting with form elements
    iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div#page iframe")))
    driver.switch_to.frame(iframe)

    # Click the confirm button "ยืนยัน"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btn_start_act"))).click()

    """Full Field Arrived & Start Time."""
    # Click select radio "isArriveAndStart"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "inlineRadio2"))).click()

    # Assign date time on text field "ArrivalDate"
    arrival_date_field = driver.find_element(By.ID, "ArrivalDate")
    arrival_date_field.send_keys(globals().get("T_Started", ""))

    # Click placeholder field instead of pressing Enter
    arrival_placeholder = driver.find_element(By.XPATH, "//*[@id='ArrivalDate']")
    arrival_placeholder.click()
    
    # Click set checked check box in "ตรวจสอบข้อมูลเรียบร้อยแล้ว"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "showSubmitWorkOrderButton"))).click()
    # Click the confirm button "ยืนยัน"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "SubmitButtonWorkOrder"))).click()

    """Full Field Finished & Depart Time and Activity Summary."""
    # Click select radio "isFinishedAndDepart2"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "isFinishedAndDepart2"))).click()

    # Assign date time on text field "FinishDate"
    arrival_date_field = driver.find_element(By.ID, "FinishDate")
    arrival_date_field.send_keys(globals().get("T_Finished", ""))

    # Click placeholder field instead of pressing Enter
    arrival_placeholder = driver.find_element(By.XPATH, "//*[@id='FinishDate']")
    arrival_placeholder.click()
    
    driver.find_element(By.ID, "finish_text").send_keys(globals().get("Activity_Summary", ""))

    # Click set checked check box in "ตรวจสอบข้อมูลเรียบร้อยแล้ว"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "showSubmitWorkOrderButton"))).click()
    # Click the confirm button "ยืนยัน"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "SubmitButtonWorkOrder"))).click()

    """Check Summary Detail."""
    # Click set checked check box in "ตรวจสอบข้อมูลเรียบร้อยแล้ว"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "showSubmitCloseWorkOrderButton"))).click()
    # Click the confirm button "ยืนยัน"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "SubmitButtonCloseWorkOrder"))).click()

    """Check Taxi Expense Detail."""
    # Click set checked check box in "ตรวจสอบข้อมูลเรียบร้อยแล้ว"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "showSubmitWorkOrderButton"))).click()
    # Click the confirm button "ยืนยัน"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "SubmitButtonWorkOrder"))).click()

    """Back To Home Page."""
    # Switch back to the main content after interacting with the iframe
    driver.switch_to.default_content()
    # Click the confirm button "ใบงานที่เกี่ยวข้อง"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='footer-bar']/a[1]"))).click()


def show_progress_popup(total):
    """Creates a popup window to show progress."""
    root = tk.Tk()
    root.title("Progress")
    root.geometry("300x100")
    root.attributes('-topmost', 1)  # Always on top
    
    progress_label = tk.Label(root, text="Processing 0/{0}".format(total))
    progress_label.pack(pady=10)
    
    progress_var = tk.IntVar()
    progress_bar = tk.ttk.Progressbar(root, orient="horizontal", length=250, mode="determinate", variable=progress_var)
    progress_bar.pack(pady=5)
    
    def update_progress(current):
        progress_label.config(text="Processing {}/{}".format(current, total))
        progress_var.set((current / total) * 100)
        root.update()
    
    return root, update_progress

def main():
    """Main workflow execution."""
    logging.info("Program execution started.")

    # If running as a PyInstaller EXE, get the directory where the EXE is located
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        # If running as a normal Python script, get the script directory
        base_path = os.path.dirname(os.path.abspath(__file__))

    key_file_path = os.path.join(base_path, "credentials.txt")  # Construct the correct path for credentials.txt
    excel_file_path = os.path.join(base_path, "Daily Task.xlsm")  # Construct the correct path for Daily Task.xlsm

    # Get username password
    username, password = get_login_credentials(key_file_path)
    logging.info("Retrieved login credentials successfully.")
    
    # Launch Excel
    launch_excel(excel_file_path)
    logging.info("Launched Excel file successfully.")
    
    # Read Excel Data
    sheet_name = "Today"
    matrix = read_excel(excel_file_path, sheet_name)
    logging.info("Read Excel data successfully.")

    total_rows = 0
    for row_idx in range(2, len(matrix)):   # Excluding header | row (index 2) to the last row of column A
        if matrix[row_idx][0] is None:  # Assuming column A is index 0
            break  # Stop looping if column A is empty
        total_rows+=1

    popup, update_progress = show_progress_popup(total_rows)

    # Login to Web CSM/MSA
    driver = login_web(username, password, "https://csm.ait.co.th/msa/login.php")
    logging.info("Logged into web CSM/MSA successfully.")

    # Loop through rows starting from the second row (index 2) to the last row of column A
    for row_idx in range(2, len(matrix)):
        if matrix[row_idx][0] is None:  # Assuming column A is index 0
            break  # Stop looping if column A is empty
        assign_variables(matrix[row_idx])
        #print("Processing row:", matrix[row_idx])  # Debugging output
        logging.info(f"Processing row {row_idx}: {matrix[row_idx][6]}")

        update_progress(row_idx - 1)
        
        # Create NEW SAR
        create_new_sar(driver)
        #module_record_expenses_continue(driver)
        logging.info(f"Executed: New SAR for row {row_idx}")
        
        # Navigate to Modules based on P_Type
        if globals().get("P_Type") == "Adhoc":
            module_adhoc(driver)
            logging.info(f"Executed: Module Adhoc for row {row_idx}")
            
        elif globals().get("P_Type") == "MA/Warranty":
            module_ma_warranty(driver)
            logging.info(f"Executed: Module MA/Warranty for row {row_idx}")
        
    # Close browser
    time.sleep(1)
    driver.quit()
    logging.info("Closed web browser successfully.")

    popup.destroy()
    logging.info("Program execution completed.")
    sys.exit(0)  # Exit program after execution
    
if __name__ == "__main__":
    main()
