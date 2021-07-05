from xml.etree import ElementTree


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
        current_key = ''
        tags = [item for item in self.tree.iter() if item.tag.find("ПланыКомпетенции") != -1]

        for current_tag in tags:
            if 'ШифрКомпетенции' in current_tag.attrib:
                competence_code = current_tag.attrib['ШифрКомпетенции']
                competence_name = current_tag.attrib['Наименование']
                if '.' in competence_code:
                    self.competences[current_key].append({competence_code: competence_name})
                else:
                    result = f"{competence_code}:{competence_name}"
                    self.competences[result] = []
                    current_key = result
        return self.competences

    def get_disciplines(self):
        tags = [item for item in self.tree.iter() if item.tag.find("ПланыСтроки") != -1]
        for tag in tags:
            discipline_name = tag.attrib['Дисциплина']
            discipline_code = tag.attrib['ДисциплинаКод']
            self.disciplines.append(f"{discipline_code} {discipline_name}")
        return self.disciplines

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


obj = Parser()

for key in obj.get_competences().keys():
    item = key.split(':')
    print(item[0])
    print(item[1])


print('Завершено')

