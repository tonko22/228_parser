import re
import json
from natasha import NamesExtractor, DatesExtractor
from natasha.markup import format_json
import logging 

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(levelname)s %(funcName)s %(message)s')

der = DatesExtractor()
ner = NamesExtractor()

class EntityExtractor():
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

    # patterns to search imprisonment
    imprisonment_patterns = [ 
        re.compile("освобожд[её]на? по отбытию срока", re.IGNORECASE),
        re.compile("освобожд[её]на? условно-досрочно", re.IGNORECASE),
        re.compile("освобожд[её]на? из колонии по постановлению", re.IGNORECASE) ]

    # drugs mass patterns
    drugs_mass_patterns = [ 
        re.compile("\.(.*?)([\d.,]+) (килогр\w+)(.*?)\.", re.IGNORECASE), 
        re.compile("\.(.*?)([\d.,]+) (грам\w+)(.*?)\.", re.IGNORECASE),
        re.compile("\.(.*?)([\d.,]+) (гр\.)(.*?)\.", re.IGNORECASE)]

    # drugs patterns
    drugs_patterns = [ 
        "гашиш", "конопля", "марихуана", "пара-метоксиметамфетамин", "фторамфетамин", "амфетамин", "экстракт маковой соломы", 
        "являющееся производным", "a-PVP", "кокаин", "героин", "6 - моноацетилморфин", "6-моноацетилморфин", "ацетилкодеин", "метадон", "МДМА", 
        "мефедрон", "спайс", "метилэфедрон", "3-метил-2 бутановой кислоты", "ACBM", "ТМСР", "AKB", "2С-В", "масло каннабиса", "AB-PINACA-CHM", 
        "метанон", "хинолин", "карфентанил", "тарен", "метиловый эфир" ]

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

    # patterns to search extenuating circumstances
    extenuating_patterns = [
        re.compile("(?:обстоятельств(?:.*?)смягчающ|смягчающ(?:.*?)обстоятельств)(?:.*?)(?:призна[её]т(?:.*?)учитывает|призна[её]т|учитывает)(?:.*?что |.*?: | )(.*)[\r\n]?", re.IGNORECASE),
        re.compile("(.*суд признает смягчающими обстоятельствами)", re.IGNORECASE) ]

    # patterns to search aggravating circumstances
    aggravating_patterns = {
        "рецидив преступлений": 
            [ "рецидив" ],
        "наступление тяжких последствий в результате совершения преступления":
            [ "тяжких последствий" ],
        ("совершение преступления в составе группы лиц, группы лиц по предварительному сговору, "
         "организованной группы или преступного сообщества(преступной организации)") : 
            [ "в составе группы", "по предварительному сговору", "организованной группы", "преступного сообщества", "преступной организации" ],
        "особо активная роль в совершении преступления": 
            [ "особо активн" ],
        ("привлечение к совершению преступления лиц, которые страдают тяжелыми психическими расстройствами либо находятся в состоянии опьянения,"
         " а также лиц, не достигших возраста, с которого наступает уголовная ответственность"):
            [ "привлечение к совершению преступления" ],
        ("совершение преступления по мотивам политической, идеологической, расовой, национальной или религиозной ненависти или вражды "
        "либо по мотивам ненависти или вражды в отношении какой-либо социальной группы;"):
            [ "ненависти", "вражды" ],
        "совершение преступления из мести за правомерные действия других лиц, а также с целью скрыть другое преступление или облегчить его совершение":
            [ "из мести", "скрыть другое преступление", "облегчить совершение" ],
        "совершение преступления в отношении лица или его близких в связи с осуществлением данным лицом служебной деятельности или выполнением общественного долга":
            [ "служебной деятельности", "выполнением общественного долга" ],
        ("совершение преступления в отношении женщины, заведомо для виновного находящейся в состоянии беременности, а также в отношении малолетнего, "
        "другого беззащитного или беспомощного лица либо лица, находящегося в зависимости от виновного"):
            [ "заведомо для виновного находящейся в состоянии беременности", "беззащитн", "беспомощн", "в зависимости от виновн" ],
        "совершение преступления с особой жестокостью, садизмом, издевательством, а также мучениями для потерпевшего":
            [ "жестокост", "садизм", "издевательств", "мучен" ],
        ("совершение преступления с использованием оружия, боевых припасов, взрывчатых веществ, взрывных или имитирующих их устройств, "
        "специально изготовленных технических средств, наркотических средств, психотропных, сильнодействующих, ядовитых и радиоактивных веществ, "
        "лекарственных и иных химико-фармакологических препаратов, а также с применением физического или психического принуждения"):
            [ "оружия", "боевых припасов", "взрывчат", "взрывн", "ядовит", "радиоактивн", "физического принуждения", "психического принуждения" ],
        ("совершение преступления в условиях чрезвычайного положения, стихийного или иного общественного бедствия, а также при массовых беспорядках,"
        " в условиях вооруженного конфликта или военных действий"):
            [ "чрезвычайного положения", "стихийного бедствия", "беспорядках", "в условиях вооруженного конфликта", "в условиях военных действий" ],
        "совершение преступления с использованием доверия, оказанного виновному в силу его служебного положения или договора":
            [ "с использованием доверия" ],
        "совершение преступления с использованием форменной одежды или документов представителя власти":
            [ "форменной одежды", "документов представителя власти" ],
        "совершение умышленного преступления сотрудником органа внутренних дел":
            [ "совершение умышленного преступления сотрудником органа внутренних дел" ],
        ("совершение преступления в отношении несовершеннолетнего (несовершеннолетней) родителем или иным лицом, на которое законом возложены "
        "обязанности по воспитанию несовершеннолетнего (несовершеннолетней), а равно педагогическим работником или другим работником образовательной"
        " организации, медицинской организации, организации, оказывающей социальные услуги, либо иной организации, обязанным осуществлять "
        "надзор за несовершеннолетним (несовершеннолетней)"):
            [ "законом возложены обязанности по воспитанию", "педагогическим работником", 
              "работником образовательной организации", "осуществлять надзор за несовершеннолетн" ],
        "совершение преступления в целях пропаганды, оправдания и поддержки терроризма":
            [ "терроризм" ],
        "совершение преступления в состоянии опьянения":
            [ "совершение преступления в состоянии опьянения" ]
        }

    def __init__(self, text):
        self.text = text
        self.paragraphs = self.text.split('\n')
        
    @property
    def court_name(self):
        """ Суд, выносящий приговор """
        try:
            match = self.court_name_pattern.search(self.text)
            return match.group(1)
        except BaseException as e:
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
            name = ner(match.group(0).strip(", -\t\r\n"))

            # if there are name matches
            if len(name.matches) > 0:

                # get names as json
                defendant_dict = name.matches[0].fact.as_json

                # if there is surname
                if "last" in defendant_dict:

                    # uppercase first letter
                    defendant_dict["last"] = defendant_dict["last"][0].upper() + defendant_dict["last"][1:]

                    # create full name
                    full_name = "{} {}.{}".format(defendant_dict["last"], defendant_dict["first"], defendant_dict["middle"])

                    # add to dict
                    defendants.append(full_name)

                # if there are no matches
                else:

                    # add regexp match to dict
                    defendants.append(match.group(1).strip(", -\t\r\n"))

            # if there are no matches
            else:

                # add regexp match to dict
                defendants.append(match.group(1).strip(", -\t\r\n"))
        except BaseException as e:
            logger.warning("Could not parse defendatns: {}".format(e))

        # return defendants list
        return ", ".join(defendants)
    
    @property
    def conviction(self):
        """ Судимость да/нет """
        return True if any(e in self.text for e in self.conviction_patterns) else \
            False if any(e in self.text for e in self.non_conviction_patterns) else None
    
    @property
    def imprisonment(self):
        """ Отбывал ли ранее лишение свободы да/нет """

        # if not convicted before, then there was no imprisonment
        if self.conviction == False:
            return False

        # iterate all imprisonment patterns
        for pattern in self.imprisonment_patterns:

            # if matches, then there was imprisonment
            if pattern.search(self.text) != None: return True

        # no information
        return None
    
    @property
    def drugs(self):
        """ Словарь {Вид наркотика: количество} """

        # zero drugs dict
        drugs = {}

        # iterate all drug mass patterns
        for pattern in self.drugs_mass_patterns:

            # search for all drug mass patterns
            matches = pattern.findall(self.text)

            # if there are matches
            if matches:

                # iterate all matches
                for match in matches:

                    # for catching exceptions on index()
                    try:

                        # get name of drug
                        name = [self.drugs_patterns[i] for i in range(len(self.drugs_patterns)) if self.drugs_patterns[i] in match[0]][0]

                        # correct name if necessary
                        if name == "является производным": name = "производное"

                    # if no drug found
                    except: continue

                    # add drug to dict
                    if name not in drugs:
                        drugs[name] = match[1] + " " + match[2]

        # if there are no matches
        if not drugs:

            # find drug patterns in the whole text
            try:

                # get index of drug
                name = [self.drugs_patterns[i] for i in range(len(self.drugs_patterns)) if self.drugs_patterns[i] in self.text][0]

                # correct name if necessary
                if name == "является производным": name = "производное"

                # add drug to dict
                drugs[name] = None

            # if no drug found
            except: return {}

        drug_stirng = ""
        for k, v in drugs.items():
            drug_stirng += "{}: {}; ".format(k, self.normalize_value(v))
        return drug_stirng

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

        # iterate all extenuating patterns
        for pattern in self.extenuating_patterns:

            # match pattern
            match = pattern.search(self.text)

            # if there is match
            if match != None and len(match.groups()) > 0:

                # return first match
                return match.group(1).strip(" \r\n,.")

        # nothing found
        return None
    
    @property
    def aggravating_circumstances(self):
        """ Отягчающие обстоятельства """

        # create zero list
        aggravating_circumstances = []

        # enumerate all aggravating patterns
        for name, patterns in self.aggravating_patterns.items():

            # if there is match, add name
            if any(e in self.text for e in patterns): aggravating_circumstances.append(name)

        # return aggravating circumstances joined by comma
        return ",".join(aggravating_circumstances) if aggravating_circumstances else None
    
    @property
    def special_order(self):
        """ Особый порядок да/нет """
        return any(e in self.text for e in self.special_order_patterns)
    
    @staticmethod
    def normalize_value(value):
        if value==False:
            return "нет"
        if value==True:
            return "да"
        if value is None:
            return "нет данных"
        else:
            return value
        
    
    @property
    def summary_dict(self):
        summary_dict = {
            "Суд": self.court_name,
            "Дата приговора": self.sentence_date,
            "ФИО": self.defendants,
            "Особый порядок": self.special_order,
            "Судимость": self.conviction,
            "Вид наказания": self.punishment_type,
            "Срок наказания в месяцах": self.punishment_duration,
            "Отбывал ли ранее лишение свободы": self.imprisonment,
            "Наркотики": self.drugs,
            "Смягчающие обстоятельства": self.extenuating_circumstances,
            "Отягчающие обстоятельства": self.aggravating_circumstances
        }
        summary_dict_normalized = {k: self.normalize_value(v) for k, v in summary_dict.items()}
        return summary_dict_normalized