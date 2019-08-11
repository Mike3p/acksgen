from wtforms import (Form, SelectField, StringField, validators, IntegerField, SubmitField, BooleanField)

#form to generate classed characters
class CharacterGenerationForm(Form):
    characterClass = SelectField(u'Class')
    characterLevel = SelectField(u'Level', choices=[(1,'1'), (2,'2'), (3,'3'), (4,'4'), (5,'5'), (6,'6'), (7,'7'), 
        (8,'8'), (9,'9'), (10,'10'), (11,'11'), (12,'12'), (13,'13'), (14,'14'), ])
    characterNumber = IntegerField(u'Number', default = 1)
    submit = SubmitField(u'Generate')
    characterPersonality = BooleanField(u'Personality', default="checked")