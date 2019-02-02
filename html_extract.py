import os
from bs4 import BeautifulSoup
import requests
import re


def validate_url(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    page = requests.get(url, headers=headers)
    return "приговор" in page.text.lower()


def get_link(site, num):
    return "https://{}/modules.php?name=sud_delo&srv_num=1&name_op=doc&number={}&delo_id=1540006&new=0&text_number=1".format(site, num)

def get_court_and_id(filename):
    try:
        site = re.search(r"([\w\.])*\.sudrf\.ru", filename).group(0) # characters and dots ending with .sudrf.ru
    except:
        site = None
    try:
        prigovor_id = re.search(r"\d+(?=\.)", filename).group(0) # any number of digits followed by a dot
    except:
        prigovor_id = None
        
    return site, prigovor_id
    
    
def get_court_name(filename):
    url, _ = get_court_and_id(filename)
    if url:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        page = requests.get("http://" + url, headers=headers).text
        soup = BeautifulSoup(page, "html.parser")

        return soup.find("title").text

    
def html_extract(filename): 

    '''
    Принимает на вход: путь на *html файл на диске
    Возвращает: 
    	txt - текст приговора,
    	link - его URL,
    	e - проверка на эксепшен, если всё прошло нормально, то там False. Если в тексте не нашлось слово "приговор", возвращает "Empty", иначе сам экспепшн

   	При ошибке поля txt и link - пустые
   	'''

    # на всякий, вдруг где-то таки юникод
    try:
        file = open(filename, encoding='cp1251', mode='r').read()
    except:
        try:
            file = open(filename, encoding='utf-8', mode='r').read()
        except Exception as e:
            return "", "", e
    
    try:
        soup = BeautifulSoup(file, "html.parser")
        text = soup.find("div", {"id" : "content"}).body.get_text()
        
        if "приговор" in text.lower():
            
            e = False # чек экспешена
            
            parserlink = re.search(r"<parserlink>(.*)</parserlink>", file)
            if parserlink:
                link = parserlink.group(1)
            else:
                filename_split = filename.split("\\")
                site = filename_split[-2]
                # избавляемся от префикса в имени файла
                num_with_prefix = filename_split[-1]
                prigovor_id = num_with_prefix.split("-")[-1].replace(".html", "")
                link = "http://{}/modules.php?name=sud_delo&srv_num=1&name_op=doc&number={}&delo_id=1540006&new=0&text_number=1".format(site, prigovor_id)
        else:
            text, link, e = "", "", "Empty"
            
        return text, link, e
    
    except Exception as e:
        return "", "", e
