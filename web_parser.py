from functools import partial
import re
import logging
import selenium as se
import requests
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import LazyProperty


logger = logging.getLogger()


class Page:
    element_css_tags = {
        "case_link" : ".resultHeader.openCardLink",
        "file_url": ".bigField"
    }
    
    re_pattern_id_from_url = "(?<=id=)(.*?)(?=&shard)" # 

    def __init__(self, url: str):
        self.url = url
        '''
        self.options = se.webdriver.ChromeOptions()
        self.options.add_argument('headless')
        self.driver = se.webdriver.Chrome(options=self.options)
        '''
        self.driver = se.webdriver.Firefox()
        self.driver.implicitly_wait(30) # timeout for slow JS requests 
        self.driver.get(self.url)
        
    def get_elements_by_css_selector(self, element_name: str):
        css_tag = self.element_css_tags.get(element_name)
        elements = self.driver.find_elements(by=By.CSS_SELECTOR, value=css_tag)
        return list(elements)

    @LazyProperty
    def case_elemenets(self) -> list:
        """ List of web-elements containing current page case urls """
        return self.get_elements_by_css_selector("case_link")
    
    
    def get_url(self, element: se.webdriver.remote.webelement.WebElement) -> str:
        """ Extract url-string from web-element """
        return element.get_attribute("href")
    
    @LazyProperty
    def current_page_case_urls(self) -> list:
        return list(map(self.get_url, self.case_elemenets))
    
    def extract_id(self, case_url: str):
        return re.search(self.re_pattern_id_from_url, case_url).group()     
    
    @LazyProperty
    def current_page_case_ids(self) -> list:
        return list(map(self.extract_id, self.current_page_case_urls))
    
    @LazyProperty
    def file_url(self):
        """ Case page 2-nd view, containing string fields only """
        return list(map(self.get_url, self.get_elements_by_css_selector("file_url")))[0]
    
    def get_case_json_dict(self, case_id: str) -> dict:
        resp = requests.post("https://bsr.sudrf.ru/bigs/showDocument.action",
                             json={"request": {"id": case_id}},
                             headers={"Content-Type": "application/json"})
        json_dict = resp.json() 
        return json_dict
    
    @LazyProperty
    def current_page_case_json_dicts(self) -> list:
        return list(map(self.get_case_json_dict, self.current_page_case_ids))
    
    def go_to_next_page(self):
        pass

class Case():
    def __init__(self, case_json):
        self.case_json = case_json
        self.case = case_json["document"]
        self.case_fields = case["fields"]
        
    def parse_field_kv(field_name: str, field_key: str) -> dict:
        return {field_name, self.case_fields[field_name[field_key]]} 
    
    @staticmethod
    def extract_values(field: dict) -> dict:
        target_values = ["value", "valueWOHL", "longValue", "dateValue"]
        return {v: field[v] for v in target_values}
        
if __name__=="__main__":
    search_page = Page(target_url)
    case_page_url = search_page.current_page_case_urls[0]
    case_page = Scraper(case_page_url)
    file_page = Scraper(case_page.file_url)