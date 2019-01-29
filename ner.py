import re
import json
from natasha import NamesExtractor, DatesExtractor
from natasha.markup import format_json

der = DatesExtractor()
ner = NamesExtractor()

class prigovorParser():
    """ All methods return parsed values in json format """
    intro_limit = 200 # first symbols to search for sentence_date
    
    court_name_pattern = re.compile("\s+(.*) в составе")
    defendant_full_name_pattern = re.compile("подсудим[огй]{2,3} (.*)[ ,\r\n]", re.MULTILINE)
    conviction_patterns = [ "ранее судим", "рецидив" ]
    non_conviction_patterns = [ "не судим" ]
    drugs_sp = re.compile("вещества:")
    special_order_patterns = [ 
        "317 Уголовно-процессуальн", 
        "316 Уголовно-процессуальн", 
        "317 УПК", 
        "316 УПК", 
        "в особом порядке",
        "без проведения судебного разбирательства" ]

    
    def __init__(self, text):
        self.text = text
        self.paragraphs = self.text.split('\n')
        
    @property
    def court_name(self):
        """ Суд, выносящий приговор """
        try:
            # search for pattern in text
            match = self.court_name_pattern.search(self.text)

            # return matched group
            return match.group(1)
        except:
            # return None
            return None
        
    @property
    def sentence_date(self):
        """ Дата приговора 
        Ищется первая дата в первых 200 символах
        """
        date_matches = der(self.text[:self.intro_limit])
        facts = [_.fact.as_json for _ in date_matches]
        if len(date_matches.as_json) > 0:
            result_dict = date_matches.as_json[0]["fact"]
            return "{}/{}/{}".format(result_dict["year"], result_dict["month"], result_dict["day"])
        else:
            return None

    
    @property
    def defendants(self):
        """ Фио подсудимых """

        # defendants list
        defendants = []
        
        try:
            # search for pattern in text
            match = self.defendant_full_name_pattern.search(self.text)

            # parse line with NamesExtractor
            name = ner(match.group(1).strip(", \t\r\n"))

            # if there are name matches
            if len(name.matches) > 0:

                # get names as json
                defendant_dict = name.matches[0].fact.as_json

                # uppercase first letter
                defendant_dict["last"] = defendant_dict["last"][0].upper() + defendant_dict["last"][1:]

                # create full name
                full_name = "{} {}.{}".format(defendant_dict["last"], defendant_dict["first"], defendant_dict["middle"])

                # add to dict
                defendants.append(full_name)

            # if there are no matches
            else:

                # add regexp match to dict
                defendants.append(match.group(1))
        except:
            # return empty list
            return []

        # return defendants list
        return defendants
    
    @property
    def conviction(self):
        """ Судимость да/нет """
        return True if any(e in self.text for e in self.conviction_patterns) else \
            False if any(e in self.text for e in self.non_conviction_patterns) else None
    
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
        return any(e in self.text for e in self.special_order_patterns)
    
    @property
    def summary_dict(self):
        summary_dict = {
            "Суд": self.court_name,
            "Дата приговора": self.sentence_date,
            "ФИО": self.defendants,
            "Особый порядок": self.special_order,
            "Судимость": self.conviction
        }
        return summary_dict