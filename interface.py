# coding=utf8
from tkinter import *
from tkinter import filedialog as fd
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import messagebox as mb
import datetime
from peewee import *
from xml.etree import ElementTree
import doc_creator
from doc_creator import *

db = SqliteDatabase('database.db')
data_obj = doc_creator.DocData()
global_dic = {}


class Parser:

    def __init__(self, xml_path="doc/data/p.xml"):
        self.xml_path = xml_path
        self.competences = {}
        self.disciplines = []
        self.profiles = []
        self.parser = ElementTree.XMLParser(encoding='utf-8')
        self.tree = ElementTree.parse("doc/data/p.xml", self.parser)

    def get_competences(self):
        current_key = ''
        tags = [item for item in self.tree.iter(
        ) if item.tag.find("ПланыКомпетенции") != -1]

        for current_tag in tags:
            if 'ШифрКомпетенции' in current_tag.attrib:
                competence_code = current_tag.attrib['ШифрКомпетенции']
                competence_name = current_tag.attrib['Наименование']
                if '.' in competence_code:
                    self.competences[current_key].append(
                        {competence_code: competence_name})
                else:
                    result = f"{competence_code} {competence_name}"
                    self.competences[result] = []
                    current_key = result
        return self.competences

    def get_disciplines(self):
        tags = [item for item in self.tree.iter(
        ) if item.tag.find("ПланыСтроки") != -1]
        for tag in tags:
            discipline_name = tag.attrib['Дисциплина']
            discipline_code = tag.attrib['ДисциплинаКод']
            self.disciplines.append(f"{discipline_code} {discipline_name}")
        return self.disciplines

    def get_profiles(self):
        tags = [item for item in self.tree.iter(
        ) if item.tag.find("псСтандарты") != -1]
        for tag in tags:
            profile_name = tag.attrib['НаименованиеВидаПрофДеятельности']
            self.profiles.append(profile_name)
        return self.profiles


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
            competence_lst.append(competence.competence_code)
        return competence_lst

    # Метод результатом которого является список дисциплин
    def get_disciplines(self):
        disciplines = []
        for item in Discipline.select().order_by(Discipline.discipline_name.asc()):
            result = f"{item.discipline_code}:{item.discipline_name}"
            disciplines.append(result)
        return disciplines

    # Метод, результатом которого является список профилей подготовки
    def get_profiles(self):
        profiles = []
        for item in Standart.select():
            profiles.append(item.name)
        return profiles

    # Метод, результатом которого является кол-во часов, форма аттестации(4 раздел) по заданной дисциплине
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
            if item.work_name not in work_types:
                work_types.append(item.work_name)
        return work_types



# Title page
def openTitle():
    def saver():
        decanDate = []
        decanDate.append(dataAllList.get())
        decanDate.append(dataAllMonthList.get())
        decanDate.append(dataAllYearList.get())
        subject = subjectsList.get()
        profile = profileList.get()
        global_dic['discipline'] = subject

        data_obj.get_title(
            decanDate[0],
            decanDate[1],
            decanDate[2],
            subject,
            profile
        )
        titleEdit.destroy()

    titleEdit = Toplevel(menu)
    titleEdit.title('ТИТУЛЬНЫЙ ЛИСТ')
    titleEdit.geometry('700x400')
    titleEdit.resizable(width=False, height=False)

    frame = Frame(titleEdit)

    months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
              'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    days = [i for i in range(1, 32)]
    years = [i for i in range(2000, 2031)]

    dataAllLabel = Label(titleEdit, text="Дата: ")
    dataAllLabel.grid(row=0, column=0, sticky="w")

    dataAllList = ttk.Combobox(titleEdit, values=days)
    dataAllList.place(x=236, y=3)
    dataAllList.config(width=5)

    dataAllMonthList = ttk.Combobox(titleEdit, values=months)
    dataAllMonthList.place(x=288, y=3)
    dataAllMonthList.config(width=10)

    dataAllYearList = ttk.Combobox(titleEdit, values=years)
    dataAllYearList.place(x=374, y=3)
    dataAllYearList.config(width=10)

    nameSubjectLabel = Label(titleEdit, text="Наименование дисциплины (модуля): ")
    nameSubjectLabel.grid(row=1, column=0, sticky="w")


    obj = DataBase()

    subjectsList = ttk.Combobox(titleEdit, values=obj.get_disciplines())
    subjectsList.place(x=236, y=23)
    subjectsList.config(width=60)

    profileLabel = Label(titleEdit, text="Направленность (профиль) подготовки: ")
    profileLabel.grid(row=2, column=0, sticky="w")
    profileList = ttk.Combobox(titleEdit, values=obj.get_profiles())
    profileList.config(width=60)
    profileList.place(x=236, y=43)

    Button(titleEdit, text="Сохранить", command=saver).grid(row=10, column=0, sticky="w")


# Objective and problems page
def openFirst():
    firstEdit = Toplevel(menu)
    firstEdit.title('I. ЦЕЛИ И ЗАДАЧИ ДИСЦИПЛИНЫ (МОДУЛЯ)')
    firstEdit.geometry('600x400')
    firstEdit.resizable(width=False, height=False)

    frame = Frame(firstEdit)

    targetLabel = Label(firstEdit, text="Цели: ")
    targetLabel.grid(row=0, column=0, sticky="w")
    target = StringVar()
    targetEntry = Entry(firstEdit, textvariable=target, width=80)
    targetEntry.grid(row=0, column=1, padx=5, pady=5)



    tasksLabel = Label(firstEdit, text="Задачи: ")
    tasksLabel.grid(row=1, column=0, sticky="w")


    def taskAdd():
        box.insert(END, tasksEntry.get())
        tasksEntry.delete(0, END)

    def taskDel():
        select = list(box.curselection())
        select.reverse()
        for i in select:
            box.delete(i)

    def taskAndTargetOutput():
        objective = target.get()
        problems = box.get(0, END)
        data_obj.get_first_chapter(objective, problems)
        firstEdit.destroy()


    box = Listbox(firstEdit, selectmode=EXTENDED, width=80)
    box.grid(row=3, column=1, sticky="w")
    scroll = Scrollbar(firstEdit, command=box.yview)
    scroll.grid(row=3, column=0, sticky="e")
    box.config(yscrollcommand=scroll.set)


    tasksEntry = Entry(firstEdit, width=80)
    tasksEntry.grid(row=1, column=1)
    Button(firstEdit, text="Добавить задачу", command=taskAdd).grid(
        row=8, column=1, sticky="n")
    Button(firstEdit, text="Удалить задачу", command=taskDel).grid(
        row=9, column=1, sticky="n")
    Button(firstEdit, text="Сохранить", command=taskAndTargetOutput).grid(
        row=10, column=1, sticky="n")
    frame.place(relwidth=0.8, relheight=0.7)


def openSecond():
    secondEdit = Toplevel(menu)
    secondEdit.title('II. МЕСТО ДИСЦИПЛИНЫ В СТРУКТУРЕ ОПОП ВО')
    secondEdit.geometry('600x400')
    secondEdit.resizable(width=False, height=False)

    frame = Frame(secondEdit)

    Descr1 = Label(secondEdit, text="2.1. Учебная дисциплина (модуль) ")
    Descr1.place(x=10, y=10)

    obj = DataBase()
    var = obj.get_disciplines()
    disc = [item.split(':')[1] for item in var]

    subjectsList = ttk.Combobox(secondEdit, values=disc)
    subjectsList.place(x=210, y=10)

    descr2 = Label(secondEdit, text="относится к части, ")
    descr2.place(x=355, y=10)

    entry1str = StringVar()
    entry1 = Entry(secondEdit, textvariable=entry1str, width=80)
    entry1.place(x=10, y=40)

    entry2str = StringVar()
    entry2 = Entry(secondEdit, textvariable=entry2str, width=80)
    entry2.place(x=10, y=70)

    descr3 = Label(secondEdit, text="Наименования дисциплин, необходимых для освоения данной учебной дисциплины:")
    descr3.place(x=10, y=100)

    entry3str = StringVar()
    subjectsList2 = Entry(secondEdit, textvariable=entry3str)
    subjectsList2.place(x=10, y=130)

    descr4 = Label(
        secondEdit,
        text="Знания и навыки, полученные обучающимися в курсе дисциплины, могут оказаться\nполезными при изучении следующих предметов:",
        justify=LEFT)
    descr4.place(x=10, y=160)

    entry3str = StringVar()
    entry3 = Entry(secondEdit, textvariable=entry3str, width=80)
    entry3.place(x=10, y=205)

    descr5 = Label(
        secondEdit,
        text="2.2. Для изучения данной учебной дисциплины (модуля) необходимы знания,\nумения и навыки, формируемые предшествующими дисциплинами:",
        justify=LEFT)
    descr5.place(x=10, y=235)

    entry4str = StringVar()
    entry4 = Entry(secondEdit, textvariable=entry4str, width=80)
    entry4.place(x=10, y=280)

    descr6 = Label(
        secondEdit,
        text="2.3. Перечень последующих учебных дисциплин, для которых необходимы знания,\nумения и навыки, формируемые данной учебной дисциплиной:",
        justify=LEFT)
    descr6.place(x=10, y=310)

    entry5str = StringVar()
    entry5 = Entry(secondEdit, textvariable=entry5str, width=80)
    entry5.place(x=10, y=355)

    def get_second_edit():
        data_obj.get_place(
            subjectsList.get(),
            subjectsList2.get(),
            entry1str.get(),
            entry2str.get(),
            entry3str.get(),
            entry4str.get(),
            entry5str.get()
        )
        secondEdit.destroy()

    Button(secondEdit, text="Сохранить", command=get_second_edit).grid(row=8, column=0, padx=5, pady=15, sticky="w")


def openThird():
    obj = DataBase()

    # Base parameters of edit
    third_edit = Toplevel(menu)
    third_edit.title('III. ТРЕБОВАНИЯ К РЕЗУЛЬТАТАМ ОСВОЕНИЯ ДИСЦИПЛИНЫ')
    third_edit.geometry('600x400')
    third_edit.resizable(width=False, height=False)


    disc_name = global_dic['discipline'].split(':')[1]
    counter = 1
    for item in obj.get_competences(disc_name):
        certification_label = Label(third_edit, text=item, font=('Ubuntu', 14))
        certification_label.grid(row=counter, column=0, sticky="w", padx=5, pady=10)
        counter += 1


def openFourth():
    # Instance of database
    obj = DataBase()
    hours = obj.get_hours(global_dic['discipline'].split(':')[1])

    # Base parameters of edit
    four_edit = Toplevel(menu)
    four_edit.title('IV. СОДЕРЖАНИЕ И СТРУКТУРА ДИСЦИПЛИНЫ')
    four_edit.geometry('600x400')
    four_edit.resizable(width=False, height=False)


    # Label of certification
    certification_label = Label(four_edit, text="Форма промежуточной аттестации: ", font=('Ubuntu', 14))
    certification_label.grid(row=0, column=0, sticky="w", padx=5, pady=10)

    # Form of certification
    certification_form = ttk.Combobox(four_edit, values=obj.get_work_type(), font=('Ubuntu', 12))
    certification_form.grid(row=1, column=0, padx=5, pady=0)
    certification_form.config(width=60)


    # Label of credit units
    credit_units_label = Label(four_edit, text="Трудоемкость дисциплины: ", font=('Ubuntu', 14))
    credit_units_label.grid(row=2, column=0, sticky="w", padx=5, pady=15)

    # Form of credit units
    credit_units_value = StringVar()
    credit_units_form = Entry(four_edit, textvariable=credit_units_value, width=60, font=('Ubuntu', 12))
    credit_units_form.grid(row=3, column=0, padx=5, pady=0, sticky="w")
    credit_units_form.insert(0, hours[0])


    # Label of all hours
    all_hours_label = Label(four_edit, text="Всего часов: ", font=('Ubuntu', 14))
    all_hours_label.grid(row=4, column=0, padx=5, pady=15, sticky="w")

    # Form of all hours
    all_hours_value = StringVar()
    all_hours_form = Entry(four_edit, textvariable=all_hours_value, width=60, font=('Ubuntu', 12))
    all_hours_form.grid(row=5, column=0, padx=5, pady=0, sticky="w")
    all_hours_form.insert(0, hours[1])


    # Label of exam hours
    exam_hours_label = Label(four_edit, text="Часы на экзамен: ", font=('Ubuntu', 14))
    exam_hours_label.grid(row=6, column=0, padx=5, pady=15, sticky="w")

    # Form of exam hours
    exam_hours_value = StringVar()
    exam_hours_form = Entry(four_edit, textvariable=exam_hours_value, width=60, font=('Ubuntu', 12))
    exam_hours_form.grid(row=7, column=0, padx=5, pady=0, sticky="w")


    def get_four_edit():
        data_obj.get_fourth_chapter(
            credit_units_value.get(),
            all_hours_value.get(),
            exam_hours_value.get(),
            certification_form.get()
        )
        four_edit.destroy()
    Button(four_edit, text="Сохранить", command=get_four_edit).grid(row=8, column=0, padx=5, pady=15, sticky="w")


def openSeventh():
    seventhEdit = Toplevel(menu)
    seventhEdit.title('VII. ОБРАЗОВАТЕЛЬНЫЕ ТЕХНОЛОГИИ')
    seventhEdit.geometry('600x400')
    seventhEdit.resizable(width=False, height=False)


    # Label of counter
    # counter_label = Label(seventhEdit, text="Введите кол-во тем: ", font=('Ubuntu', 14))
    # counter_label.grid(row=0, column=0, padx=5, pady=0, sticky="w")
    #
    # counter = StringVar()
    # exam_hours_form = Entry(seventhEdit, textvariable=counter, width=60, font=('Ubuntu', 12))
    # exam_hours_form.grid(row=1, column=0, padx=5, pady=0, sticky="w")
    #
    # def add_table(counter):
    #     for i in range(int(counter)):
    #         table_str_label = Label(seventhEdit, text="Введите данные: : ", font=('Ubuntu', 14))
    #         table_str_label.grid(row=2, column=0, padx=5, pady=0, sticky="w")
    #         str = StringVar()
    #         table_str_form = Entry(seventhEdit, textvariable=str, width=60, font=('Ubuntu', 12))
    #         table_str_form.grid(row=3, column=0, padx=5, pady=0, sticky="w")
    #
    # Button(seventhEdit, text="Создать", command=add_table(counter)).grid(row=7, column=0, padx=5, pady=15, sticky="w")


def create_doc():
    data_obj.send_data()
    print('[+] Success')


if __name__ == '__main__':
    menu = Tk()
    menu.title('Разделы')
    menu.geometry('600x400')
    menu.resizable(width=False, height=False)

    frame = Frame(menu)

    MenuLabel = Label(menu, text="Разделы РПД: ", font=('Ubuntu', 14)).grid(row=0, column=0, sticky="w", padx=5, pady=10)


    titleBtn = Button(menu, text="ТИТУЛЬНЫЙ ЛИСТ",
                      command=openTitle, bg="#127545", fg="white").grid(row=1, column=0, sticky="w", padx=5, pady=10)


    firstBtn = Button(menu, text="I. ЦЕЛИ И ЗАДАЧИ ДИСЦИПЛИНЫ (МОДУЛЯ)",
                      command=openFirst, bg="#127545", fg="white").grid(row=2, column=0, sticky="w", padx=5, pady=10)


    secondBtn = Button(menu, text="II. МЕСТО ДИСЦИПЛИНЫ В СТРУКТУРЕ ОПОП ВО",
                       command=openSecond, bg="#127545", fg="white").grid(row=3, column=0, sticky="w", padx=5, pady=10)


    thirdBtn = Button(menu, text="III. ТРЕБОВАНИЯ К РЕЗУЛЬТАТАМ ОСВОЕНИЯ ДИСЦИПЛИНЫ",
                      command=openThird, bg="#127545", fg="white").grid(row=4, column=0, sticky="w", padx=5, pady=10)


    fourthBtn = Button(menu, text="IV. СОДЕРЖАНИЕ И СТРУКТУРА ДИСЦИПЛИНЫ",
                       command=openFourth, bg="#127545", fg="white").grid(row=5, column=0, sticky="w", padx=5, pady=10)

    fifthBtn = Button(menu, text="V. УЧЕБНО-МЕТОДИЧЕСКОЕ И ИНФОРМАЦИОННОЕ ОБЕСПЕЧЕНИЕ ДИСЦИПЛИНЫ (МОДУЛЯ)",
                      command=openSeventh, bg="#127545", fg="white").grid(row=6, column=0, sticky="w", padx=5, pady=10)

    Button(menu, text="Создать документ", command=create_doc).grid(row=8, column=0, padx=5, pady=15, sticky="w")

    frame.place(relwidth=0.8, relheight=0.7)

    menu.mainloop()
