import csv
import os
import pandas as pd
import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup, SoupStrainer
from numpy import NaN
import pandas as pd
import json
import string
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#setting selenium config
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(r"https://www.azcleanelections.gov/arizona-elections/find-my-candidates")

#interacting with view all candidates button
candidates_button = driver.find_element(By.CSS_SELECTOR, value=r"button.pill:nth-child(4)")
candidates_button.click()

#parsing data
WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".people")))
main_sections = driver.find_elements(By.XPATH, "//*[contains(@id, 'secB')]")

candidates_list = []
for section in main_sections:
    branch = section.find_element(By.TAG_NAME, "h3").text
    print(branch)
    sub_sections = section.find_elements(By.TAG_NAME, value="section")

    for section in sub_sections:
        try :
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.TAG_NAME, "h3")))
            position = section.find_element(By.TAG_NAME, "h3").text
        except:
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.TAG_NAME, "h4")))
            position = section.find_element(By.TAG_NAME, "h4").text
        position_candidates = section.find_elements(By.TAG_NAME, "li")
        
        candidates_information = []
        for candidate in position_candidates:
            candidate_dict = dict(
                name = '',
                position = '',
                party = '',
                funding = '',
                image = '',
            )

            #parsing cadidate's 'basic' information: name, position, party, funding and image link
            information = candidate.text.split("<br></br>")[0].split('\n')
            information = list(filter(None, information))
            img_src = candidate.find_element(By.TAG_NAME, "img").get_attribute("src")

            information.append(img_src)

            candidate_dict["name"] = information[0]
            candidate_dict["position"] = information[1]
            candidate_dict["party"] = information[2]
            candidate_dict["funding"] = information[3]
            candidate_dict["image"] = information[4]

            candidates_information.append(information)
            
            #opening candidate's modal
            open_modal_button = WebDriverWait(candidate, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a")))
            
            open_modal_button.click()

            #parsing candidate's 'additional' information: contact information, biography, statement
            popup_modal = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#divPopup")))
            candidate_popup_information = popup_modal.find_elements(By.TAG_NAME, value="p")

            #parsing contact information
            for field in candidate_popup_information[1::]:
                field_name = field.find_element(By.TAG_NAME, 'b').text
                try: 
                    field_content = field.find_element(By.TAG_NAME, 'a').text
                except:
                    field_content = field.get_attribute('innerHTML').split('<br>')[1].replace('\n', '')
                
                candidate_dict[field_name] = field_content

            candidates_list.append(candidate_dict)
            #parsing biography and statements
            # information.append([popup_information.text for popup_information in candidate_popup_information])
            
            # candidates_information.extend(information)
        
            #closing modal
            close_modal_button = popup_modal.find_element(By.CSS_SELECTOR, value="a")
            close_modal_button.click()

            print("Estimated Progress: ",len(candidates_list)/190*100,'%')




candidates_df = pd.DataFrame(candidates_list)

print(candidates_df)

candidates_df.to_csv("candidates.csv")


# print(candidates_information[0])
