import re
import json
from natasha import NamesExtractor, DatesExtractor
from natasha.markup import format_json

der = DatesExtractor()
ner = NamesExtractor()

class prigovorParser():
    """ All methods return parsed values in json format """
    intro_limit = 200 # first symbols to search for sentence_date
    
    court_name_pattern = re.compile("в составе")
    defendant_full_name_pattern = re.compile("подсудимой|подсудимого")
    drugs_sp = re.compile("вещества:")
    
    def __init__(self, text):
        self.text = text
        self.paragraphs = self.text.split('\n')
        
    @property
    def court_name(self):
        """ Суд, выносящий приговор """
        for i, line in enumerate(self..paragraphs[:6]):
            found = prigovorParser.court_name_pattern.search(line)
            if found:
                return doc_parser.paragraphs[i][:found.start()]+"суд"
        
    @property
    def sentence_date(self):
        """ Дата приговора 
        Ищется первая дата в первых 200 символах
        """
        date_matches = der(text[:self.intro_limit])
        facts = [_.fact.as_json for _ in date_matches]
        result_dict = date_matches.as_json[0]["fact"]
        return "{}/{}/{}".format(result_dict["year"], result_dict["month"], result_dict["day"])

    
    @property
    def defendants(self):
        """ Фио подсудимых """
        defendants = []
        for i, line in enumerate(doc_parser.paragraphs):
            found = prigovorParser.defendant_full_name_pattern.search(line)
            if found:
                defendant_dict = ner(line).matches[0].fact.as_json
                first_letter = defendant_dict["last"][0]
                if first_letter.islower():
                    defendant_dict["last"] = first_letter.upper() + defendant_dict["last"][1:]
                full_name = "{} {}.{}".format(defendant_dict["last"], defendant_dict["first"], defendant_dict["middle"])
                defendants.append(full_name)
        return defendants
    
    @property
    def conviction(self):
        """ Судимость да/нет """
        return
    
    @property
    def imprisonment(self):
        """ Отбывал ли ранее лишение свободы да/нет """
        return
    
    @property
    def drugs(self):
        """ Словарь {Вид наркотика: количество} """
        return
    
    @property
    def punishment_type(self):
        """ Вид наказания (лишение свободы/ условное лишение свободы) """
        return
    
    @property
    def punishment_duration(self):
        """ Срок наказания в месяцах """
        return

    @property
    def extenuating_circumstances(self):
        """ Смягчающие обстоятельства """
        return
    
    @property
    def aggravating_circumstances(self):
        """ Отягчающие обстоятельства """
        return
    
    @property
    def special_order(self):
        """ Особый порядок да/нет """
        return       
    
    @property
    def summary_dict(self):
        summary_dict = {
            "Суд": self.court_name,
            "Дата приговора": self.sentence_date,
            "ФИО": self.defendants
        }
        return summary_dict
