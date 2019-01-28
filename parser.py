import re
from natasha import NamesExtractor, DatesExtractor
from natasha.markup import format_json

der = DatesExtractor()
ner = NamesExtractor()

class Parser():
    """ All methods return parsed values in json format """
    intro_limit = 200 # first symbols to search for sentence_date
    court_name_search_pattern = re.compile("в составе")
    
    def __init__(self, text):
        self.text = text
    
    @property
    def court_name(self):
        """ Суд, выносящий приговор """
        match = search_pattern.search(test_str)
        test_str[:match.start()].strip()
        return
    
    @property
    def sentence_date(self):
        """ Дата приговора """
        date_matches = der(text[:self.intro_limit])
        facts = [_.fact.as_json for _ in date_matches]
        return format_json(facts)
    
    @property
    def full_name(self):
        """ Фио """
        return
    
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