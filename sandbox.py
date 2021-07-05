from peewee import *
from xml.etree import ElementTree


db = SqliteDatabase('database.db')


class Parser:

    def __init__(self):
        self.xml_path = "doc/data/p.xml"
        self.competences = {}
        self.discipline_content = {}
        self.disciplines = []
        self.profiles = []
        self.parser = ElementTree.XMLParser(encoding='utf-8')
        self.tree = ElementTree.parse(self.xml_path, self.parser)

    def get_competences(self):
        tags = [item for item in self.tree.iter() if item.tag.find("ПланыКомпетенции") != -1]
        competences = []

        for current_tag in tags:
            if 'ШифрКомпетенции' in current_tag.attrib:
                code = current_tag.attrib['Код']
                code_oop = current_tag.attrib['КодООП']
                competence_code = current_tag.attrib['ШифрКомпетенции']
                competence_name = current_tag.attrib['Наименование']
                competences.append([code, code_oop, competence_code, competence_name])
        return competences

    def get_disciplines(self):
        tags = [item for item in self.tree.iter() if item.tag.find("ПланыСтроки") != -1]
        disciplines = []
        for tag in tags:
            code = tag.attrib['Код']
            plane_code = tag.attrib['КодПлана']
            oop_code = tag.attrib['КодООП']
            block_code = tag.attrib['КодБлока']
            discipline_name = tag.attrib['Дисциплина']
            discipline_code = tag.attrib['ДисциплинаКод']
            hours_in_zet = tag.attrib['ЧасовВЗЕТ']
            hours_po_zet = tag.attrib['ЧасовПоЗЕТ']
            disciplines.append([code, plane_code, oop_code, block_code, discipline_name, discipline_code, hours_in_zet, hours_po_zet])
        return disciplines

    def get_profiles(self):
        tags = [item for item in self.tree.iter() if item.tag.find("псСтандарты") != -1]
        for tag in tags:
            profile_name = tag.attrib['НаименованиеВидаПрофДеятельности']
            self.profiles.append(profile_name)
        return self.profiles

    # ЧасовПоЗЕТ = всего часов,Трудоемкость = ЧасовПоЗЕТ / ЧасовВЗЕТ,
    def get_discipline_content(self, discipline_name):
        tags = [item for item in self.tree.iter() if item.tag.find("ПланыСтроки") != -1]
        for tag in tags:
            if tag.attrib['Дисциплина'] == discipline_name:
                all_hours = tag.attrib['ЧасовПоЗЕТ']
                labour = int(all_hours) // int(tag.attrib['ЧасовВЗЕТ'])
                self.discipline_content['ВсегоЧасов'] = all_hours
                self.discipline_content['Трудоемкость'] = labour
                return self.discipline_content

    def get_discipline_competence(self):
        tags = [item for item in self.tree.iter() if item.tag.find("ПланыКомпетенцииДисциплины") != -1]
        result = []
        for tag in tags:
            comp_code = tag.attrib['КодКомпетенции']
            disc_code = tag.attrib['КодСтроки']
            result.append([comp_code, disc_code])
        return result

    def get_work_type(self):
        tags = [item for item in self.tree.iter() if item.tag.find("СправочникВидыРабот") != -1]
        work_types = []
        for tag in tags:
            code = tag.attrib['Код']
            name = tag.attrib['Название']
            if 'КодТипРабот' in tag.attrib.keys():
                code_work_type = tag.attrib['КодТипРабот']
            else:
                code_work_type = ''
            abbreviation = tag.attrib['Аббревиатура']
            work_types.append([code, name, code_work_type, abbreviation])
        return work_types


class BaseModel(Model):
    class Meta:
        database = db


# Модель - компетенции
class Competence(BaseModel):
    code = CharField()
    oop_code = CharField()
    competence_code = CharField()
    competence_name = TextField()


# Модель - дисциплины
class Discipline(BaseModel):
    code = CharField()
    plane_code = CharField()
    oop_code = CharField()
    block_code = CharField()
    discipline_name = CharField()
    discipline_code = CharField()
    hours_in_zet = CharField()
    hours_po_zet = CharField()


# Модель - КомпетенцииДисциплины
class CompetenceDiscipline(BaseModel):
    competence_code = CharField()
    discipline_code = CharField()


# Модель - профиль подготовки
class Standart(BaseModel):
    code = CharField()
    group_code = CharField()
    name = CharField()
    purpose = TextField()


# Модель - СправочникВидыРабот
class ReferenceTypesWork(BaseModel):
    code = CharField()
    work_name = CharField()
    code_type_work = CharField()
    abbreviation = CharField()


class DataBase(BaseModel):

    # Метод, результатом которого является список компетенций по заданной дисциплине
    def get_competences(self, disc_name):
        competence_lst = []
        disc_code = Discipline.select().where(Discipline.discipline_name == disc_name).get().code
        for item in CompetenceDiscipline.select().where(CompetenceDiscipline.discipline_code == disc_code):
            competence = Competence.get(Competence.code == item.competence_code)
            competence_lst.append({competence.competence_code: competence.competence_name})
        return competence_lst

    # Метод результатом которого является список дисциплин
    def get_disciplines(self):
        disciplines = {}
        for item in Discipline.select():
            disciplines[item.discipline_name] = item.discipline_code
        return disciplines

    # Метод, результатом которого является список профилей подготовки
    def get_profiles(self):
        profiles = []
        for item in Standart.select():
            profiles.append(item.name)
        return profiles

    # Метод, результатом которого является список времени
    def get_hours(self, disc_name):
        hours = []
        for item in Discipline.select().where(Discipline.discipline_name == disc_name):
            all_hours = item.hours_po_zet
            exam_hours = item.hours_in_zet
            credit_units = int(all_hours) // int(exam_hours)
            hours.append(credit_units)
            hours.append(all_hours)
            hours.append(exam_hours)
        return hours

    def get_work_type(self):
        work_types = []
        for item in ReferenceTypesWork.select().where(ReferenceTypesWork.code_type_work == '7').order_by(ReferenceTypesWork.work_name.asc()):
            work_types.append(item.work_name)
        return work_types


db.connect()
obj = DataBase()
res = obj.get_work_type()

print('Завершено')
