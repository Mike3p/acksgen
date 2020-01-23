from wtforms import (Form, SelectField, StringField, validators, IntegerField, SubmitField, BooleanField, TextAreaField)

#form to generate classed characters
class CharacterGenerationForm(Form):
    characterClass = SelectField(u'Class')
    characterLevel = SelectField(u'Level', choices=[(0, '0'), (1,'1'), (2,'2'), (3,'3'), (4,'4'), (5,'5'), (6,'6'), (7,'7'),
        (8,'8'), (9,'9'), (10,'10'), (11,'11'), (12,'12'), (13,'13'), (14,'14'), ])
    characterNumber = IntegerField(u'Number', default = 1)
    submit = SubmitField(u'Generate')
    rollForParty = BooleanField(u'Personality')
    ethnicity = SelectField(u'Ethnicity')


class InitiativeForm(Form):
    initiativeInput = TextAreaField(u'Initiative')