

import selenium
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import date, timedelta
import pdb




options = ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome("./chromedriver", options=options)
start_url = 'http://mrcc.isws.illinois.edu/CLIMATE/'
driver.get(start_url)

try:
  WebDriverWait(driver, 600).until(EC.presence_of_element_located((By.NAME, 'textName')))
  email_field = driver.find_element_by_name('textName')
  email_field.clear()
  email_field.send_keys('Mark.Empey@ghd.com')
  pwd_field = driver.find_element_by_name('textPwd')
  pwd_field.clear()
  pwd_field.send_keys('windrose')
  driver.find_element_by_name('Submit').click()
  try:
    WebDriverWait(driver, 600).until(EC.presence_of_element_located((By.NAME, 'chStn')))
    hourly_url = 'http://mrcc.isws.illinois.edu/CLIMATE/stnhourly1.jsp'
    driver.get(hourly_url)
    try:
      WebDriverWait(driver, 600).until(EC.presence_of_element_located((By.NAME, 'Submit2')))
      driver.find_element_by_name('Submit2').click()
      try:
        WebDriverWait(driver, 600).until(EC.presence_of_element_located((By.NAME, 'state')))
        driver.find_element_by_id('co').click()
        driver.find_element_by_xpath("//select[@name='state']/option[text()='Wisconsin']").click()
        try:
          WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.NAME, "selectCounty")))
          time.sleep(5)
          driver.find_element_by_xpath("//select[@name='selectCounty']/option[text()='DOUGLAS']").click()
          driver.find_element_by_xpath("//input[@value='Update']").click()
          try:
            WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.NAME, "Submit")))
            driver.find_element_by_xpath("//input[@value='Go']").click()
            windrose_url = 'http://mrcc.isws.illinois.edu/CLIMATE/Hourly/WindRose.jsp'
            driver.get(windrose_url)
            driver.find_element_by_id('custom').click()
            yesterday = date.today() - timedelta(1)
            month = yesterday.strftime("%B")
            day = yesterday.strftime("%d")
            time.sleep(1)
            driver.find_element_by_xpath("//select[@name='mo1']/option[text()='" + month + " ']").click()
            driver.find_element_by_xpath("//select[@name='dy1']/option[text()='" + day + "']").click()
            driver.find_element_by_xpath("//select[@name='mo2']/option[text()='" + month + " ']").click()
            driver.find_element_by_xpath("//select[@name='dy2']/option[text()='" + day + "']").click()
            driver.find_element_by_xpath("//select[@name='WsMon']/option[text()='" + month + "']").click()
            driver.find_element_by_xpath("//select[@name='WsDay']/option[text()='" + day + "']").click()
            driver.find_element_by_xpath("//select[@name='WeMon']/option[text()='" + month + "']").click()
            driver.find_element_by_xpath("//select[@name='WeDay']/option[text()='" + day + "']").click()
            driver.find_element_by_name('GetClimateData').click()
            try:
              time.sleep(5)
              WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CLASS_NAME, 'highcharts-button')))
              driver.find_element_by_class_name('highcharts-button').click()
              driver.find_element_by_xpath("//div[text()='Download PNG image']").click()
              time.sleep(10)
            except Exception as e1:
              pdb.set_trace()
              print "Download button does not exist"
          except Exception as e2:
            pdb.set_trace()
            print "Go button not found"
        except Exception as e3:
          print "county select box not found"
      except Exception as e4:
        print "state select box not found"
    except Exception as e5:
      print "Next button not found"
  except Exception as e6:
    print "Station button not found"
except Exception as e7:
  print "Log in page not found"


driver.close()


