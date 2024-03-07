from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, DateField, IntegerField
from wtforms.validators import DataRequired, Length

class NewWeldForm(FlaskForm):
    new_weld_spool = StringField("spool", validators=[DataRequired(), Length(max = 20)])
    new_weld_weld = StringField("weld", validators=[DataRequired()])
    new_weld_size = IntegerField("size", validators=[DataRequired()])
    new_weld_thick = StringField("thick", validators=[DataRequired()])
    new_weld_type = StringField("type", validators=[DataRequired()])
    new_weld_welder = StringField("welder")
    new_weld_weld_date = DateField("weld_date")
    new_weld_vt = StringField("vt")
    new_weld_vt_date = DateField("vt_date")
    new_weld_nde_number = StringField("nde_number")
    new_weld_nde_date = DateField("nde_date")
    
    submit = SubmitField("Submit weld")

class CommentForm(FlaskForm):
    comment = StringField("Comment")
    submit = SubmitField("Submit comment")