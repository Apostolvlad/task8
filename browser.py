
import os
import time

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import subprocess

# from browser import Browser
class Browser():
    def __init__(self): #'C:\\Program Files\\Opera\\launcher.exe'
        self.driver_options = webdriver.ChromeOptions()
        self.driver_options.add_argument('--ignore-certificate-errors')
        self.driver_options.add_argument('--ignore-ssl-errors')
        self.driver_options.add_argument('--log-level=3')

        # Для By
        # ['CLASS_NAME', 'CSS_SELECTOR', 'ID', 'LINK_TEXT', 'NAME', 'PARTIAL_LINK_TEXT', 'TAG_NAME', 'XPATH']
        
        #self.app = GLOBAL_PATH+ 'browser\\chrome.exe'
        
    def set_show(self, mode = True):
        self.driver_options.set_headless(mode)

    def set_profile(self, path = ''):
        self.path = path
        if path == '': path = ''.join(["C:\\Users\\", os.getlogin(), "\\AppData\\Local\\Google\\Chrome\\User Data"])
        path = '--user-data-dir=' + path
        self.driver_options.add_argument(path)
    
    def create_wait(self, sleep): self.wait = WebDriverWait(self.driver, sleep)

    @property
    def options(self):
        return self.driver_options.arguments

    def _run(self):
        #self.driver_options.binary_location = self.app #'D:\\project\\python project\\утилиты для себя на пк\\бот для хроники хаоса\\на башню\\bot for autorun tower\\chrome\\bin\\chrome.exe'
        subprocess.call("TASKKILL /f  /IM  CHROME.EXE")
        subprocess.call("TASKKILL /f  /IM  CHROMEDRIVER.EXE")
        self.driver = webdriver.Chrome(options=self.driver_options)
        self.driver.set_page_load_timeout(30)
        self.set_max()
        #self.driver = webdriver.Chrome(chrome_options=self.driver_options, executable_path=GLOBAL_PATH + 'chromedriver.exe')
    
    def run(self):
        for _ in range(3):
            try:
                self._run()
                break
            except Exception as e:
                print('Error run browser: ', e)

    def set_max(self):
        self.driver.set_window_size(3000, 3000)#self.driver.maximize_window()#self.driver.set_window_size(3000, 3000)#1920,1080)#self.driver.maximize_window()

    def quit(self):
        try:
            self.driver.quit()
        except:
            print('нечего закрывать...')

    def get(self, url):
        self.driver.get(url)

    def find_element_by_xpath(self, xpath):
        return self.driver.find_element_by_xpath(xpath)

    def move_element(self, element):
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        
    def click_element(self, element):
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        actions.click().perform()
    
    def ctrlA(self, element, value):
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click(element).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(value).perform()

    def url(self):
        return self.driver.current_url 
    
    def screen(self):
        self.driver.save_screenshot('test.png')
    
    def wait_click(self, element):
        return self.wait.until(EC.element_to_be_clickable(element))
    
    def wait_watch(self, element):
        return self.wait.until(EC.visibility_of_element_located(element))
    

if __name__ == "__main__":
    b = Browser()
    try:
        b.run()
    except Exception as e:
        print('ERROR: ', e)
    finally:
        b.quit()
        input('Введите enter для завершения работы...')
