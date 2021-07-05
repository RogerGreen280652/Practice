from docxtpl import DocxTemplate


class DocCreator:
    def __init__(self):
        self.template_path = './documents/template.docx'
        self.result_path = './documents/Б1.В.12 Языки разметки сетевого контента - пример РПД.docx'
        self.temp_doc = DocxTemplate(self.template_path)

    def create_part(self, context):
        self.temp_doc.render(context)
        self.temp_doc.save(self.result_path)


class DocData:

    def __init__(self):
        self.obj = DocCreator()

        # Title list
        # Parameters of date
        self.day = None
        self.month = None
        self.year = None
        # Parameters of module
        self.discipline = None
        self.profile = None

        # First chapter
        # Objectives of discipline
        self.objective = None
        # Problems of discipline
        self.problems = None

        # Third chapter
        self.competences_indicators = None

        # Fourth chapter
        self.credit_units = None
        self.all_hours = None
        self.exam_hours = None
        self.certification_form = None

        self.context = {}

    def get_title(self, day, month, year, discipline, profile):
        self.day = day
        self.month = month
        self.year = year
        self.discipline = discipline
        self.profile = profile

        self.context['day'] = day
        self.context['month'] = month
        self.context['year'] = year
        self.context['discipline'] = discipline
        self.context['profile'] = profile

    def get_first_chapter(self, objective, problems):
        self.objective = objective
        self.problems = problems

        self.context['objective'] = objective
        self.context['problems'] = problems

    def get_second_chapter(self, competence, indicators):
        self.competences_indicators = competence
        self.context['comp'] = competence
        self.context['indicators'] = indicators

    def get_fourth_chapter(self, credit_units, all_hours, exam_hours="", certification_form=""):
        self.credit_units = credit_units
        self.all_hours = all_hours
        self.exam_hours = exam_hours
        self.certification_form = certification_form
        self.context['creditUnits'] = self.credit_units
        self.context['allHours'] = self.all_hours
        self.context['examHours'] = self.exam_hours
        self.context['certificationForm'] = self.certification_form

    def send_data(self):
        self.obj.create_part(self.context)

