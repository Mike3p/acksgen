from wtforms import (Form, SelectField, StringField, validators, IntegerField, SubmitField, BooleanField, TextAreaField, FloatField)

#form to generate classed characters
class CharacterGenerationForm(Form):
    characterClass = SelectField(u'Class')
    characterLevel = SelectField(u'Level', choices=[(0, '0'), (1,'1'), (2,'2'), (3,'3'), (4,'4'), (5,'5'), (6,'6'), (7,'7'),
        (8,'8'), (9,'9'), (10,'10'), (11,'11'), (12,'12'), (13,'13'), (14,'14'), ])
    characterNumber = IntegerField(u'Number', default = 1)
    submit = SubmitField(u'Generate')
    rollForParty = BooleanField(u'Personality')
    ethnicity = SelectField(u'Ethnicity')
    loadCharacter = TextAreaField(u'Load Character')
    createExcelSheet = BooleanField(u'create Excel Sheet')


class InitiativeForm(Form):
    initiativeInput = TextAreaField(u'Initiative')

class DomainForm(Form):
    strongholdValue = IntegerField(u'Number', default = 1)
    agriculturalInvestments = IntegerField(u'Number', default = 1)
    numberFamilies = IntegerField(u'Number', default = 1)
    averageLandValue = FloatField(u'Number', default= 6)
    taxes = IntegerField(u'Number', default= 2)
    tithes = IntegerField(u'Number', default= 1)
    liturgies = IntegerField(u'Number', default= 1)
    tributeIncome = IntegerField(u'Number', default= 0)
    tributeExpense = IntegerField(u'Number', default= 0)
    wtroopsOnGarrisonWage = IntegerField(u'Number', default= 2)
    rulerCharisma = IntegerField(u'Number', default= 2)
    rulerAuthority = IntegerField(u'Number', default= 2)
    rulerLeadership = BooleanField(u'Leadership')
    domainType = SelectField(u'Domain Type', choices=[('wilderness''wilderness'), ('borderlands', 'borderlands'), ('civilized', 'civilized')])