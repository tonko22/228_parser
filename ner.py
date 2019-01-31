import re
import json
from natasha import NamesExtractor, DatesExtractor
from natasha.markup import format_json
import logging 

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(levelname)s %(funcName)s %(message)s')


der = DatesExtractor()
ner = NamesExtractor()

class prigovorParser():
    """ All methods return parsed values in json format """
    intro_limit = 200 # first symbols to search for sentence_date

    # pattern to search court name
    court_name_pattern = re.compile("\s+(.*) в составе")

    # pattern to search defendant's name
    defendant_full_name_pattern = re.compile("подсудим[огй]{2,3} (.*)[ ,\r\n]", re.MULTILINE)

    # patterns to search conviction
    conviction_patterns     = [ "ранее судим", "рецидив" ]
    non_conviction_patterns = [ "не судим" ]

    # patterns to search sentence
    sentence_patterns = re.compile("приговорил|П Р И Г О В О Р И Л", re.IGNORECASE)

    # patterns to search suspended sentence
    suspended_sentence_patterns = [ "условн", " 73 " ]

    # pattern to search punishment
    punishment_patterns = [
        re.compile(("виновн[ымой]{2} в совершении(?:.*?)наказание(?:.*?)(один|два|три|четыре|пять|шесть|семь|восемь|девять|десять)(?:.*?)(?:год|лет)" \
            "(?:(?:.*?)(один|два|три|четыре|пять|шесть|семь|восемь|девять|десять|одиннадцать|двенадцать)(?:.*?)(?:месяц))?(?:.*?)\."), re.IGNORECASE),
        re.compile("виновн[ымой]{2} в совершении(?:.*?)наказание(?:.*?)(\d+)(?:.*?)(?:год|лет)(?:(?:.*?)(\d+)(?:.*?)(?:месяц))?(?:.*?)\.", re.IGNORECASE) ]

    # russian numbers
    russian_numbers = [ "ноль", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять", "десять", "одиннадцать", "двенадцать" ]

    # pattern to search drugs
    drugs_sp = re.compile("вещества:")

    # patterns to search special order
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
            match = self.court_name_pattern.search(self.text)
            return match.group(1)
        except:
            logger.warning("Не удалось извлечь название суда")
        
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
    def punishment(self):
        """ Вид наказания (лишение свободы/ условное лишение свободы) и срок """

        # zero results
        punishment_type     = ""
        punishment_duration = 0

        # search sentence pattern
        sentence_match = self.sentence_patterns.search(self.text)

        # if there is no sentence pattern
        if sentence_match == None: return None, None

        # get type of sentence - suspended or not
        punishment_type = "Условное лишение свободы" \
            if all(e in self.text[sentence_match.start():] for e in self.suspended_sentence_patterns) \
            else "Лишение свободы"

        # if there is match
        if sentence_match != None:

            # years and months
            years  = 0
            months = 0

            # iterate all punishment patterns
            for i in range(len(self.punishment_patterns)):

                # search punishment
                punishment_match = self.punishment_patterns[i].search(self.text[sentence_match.start():])

                # if there is match
                if punishment_match != None:

                    # check for exceptions
                    try:

                        # check for first group prescense
                        if len(punishment_match.groups()) == 0: continue

                        # get years
                        years = int(punishment_match.group(1)) if i == 1 else self.russian_numbers.index(punishment_match.group(1).lower())

                        # if second group exist
                        if punishment_match.group(2) != None:

                            # get months
                            months = int(punishment_match.group(2)) if i == 1 else self.russian_numbers.index(punishment_match.group(2).lower())

                        # print(punishment_match.group(0))
                        # print("Years: ", years)
                        # print("Months: ", months)

                        # set punishment duration
                        punishment_duration = years * 12 + months

                        break

                    # continue in case of exception
                    except: continue

        # return type and duration
        return punishment_type, punishment_duration
    
    @property
    def punishment_type(self):
        """ Вид наказания (лишение свободы/ условное лишение свободы) """

        # extract info about punishment
        p_type, p_duration = self.punishment

        # return punishment type
        return p_type
    
    @property
    def punishment_duration(self):
        """ Срок наказания в месяцах """

        # extract info about punishment
        p_type, p_duration = self.punishment

        # return punishment duration
        return p_duration

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
            "Судимость": self.conviction,
            "Вид наказания": self.punishment_type,
            "Срок наказания в месяцах": self.punishment_duration
        }
        return summary_dict
