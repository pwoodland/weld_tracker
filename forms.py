from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, DateField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

class NewWeldForm(FlaskForm):
    new_weld_spool = StringField("spool", validators=[DataRequired(), Length(max = 20)])
    new_weld_weld = StringField("weld", validators=[DataRequired()])
    new_weld_size = IntegerField("size", validators=[DataRequired()])
    new_weld_thick = StringField("thick", validators=[DataRequired()])
    new_weld_type = StringField("type", validators=[DataRequired()])
    new_weld_welder = StringField("welder", validators=[Optional()])
    new_weld_weld_date = DateField("weld_date", validators=[Optional()])
    new_weld_vt = StringField("vt", validators=[Optional()])
    new_weld_vt_date = DateField("vt_date", validators=[Optional()])
    new_weld_nde_number = StringField("nde_number", validators=[Optional()])
    new_weld_nde_date = DateField("nde_date", validators=[Optional()])
    
    submit = SubmitField("Submit weld")

class NewSpoolForm(FlaskForm):
    new_spool_line_number = StringField("line", validators=[DataRequired(), Length(max=200)])
    new_spool_dwg_number = StringField("drawing", validators=[DataRequired(), Length(max=200)])
    new_spool_rev_number = StringField("revision", validators=[DataRequired(), Length(max=10)])
    new_spool_line_spec = StringField("spec", validators=[DataRequired(), Length(max=20)])
    new_spool_spool = StringField("spool", validators=[DataRequired(), Length(max=20)])
    new_spool_dwg_date = DateField("dwg_date", validators=[Optional()])
    new_spool_welded_date = DateField("weld_date", validators=[Optional()])
    new_spool_nde_date = DateField("nde_date", validators=[Optional()])
    new_spool_pwht_date = DateField("pwht_date", validators=[Optional()])
    new_spool_hydro_date = DateField("hydro_date", validators=[Optional()])

    submit = SubmitField("Submit spool")

class MassWeldForm(FlaskForm):
    welds_text_area = TextAreaField("welds_csv", validators=[DataRequired()])
    submit = SubmitField("Submit welds")

class MassSpoolForm(FlaskForm):
    spools_text_area = TextAreaField("spools_csv", validators=[DataRequired()])
    submit = SubmitField("Submit spool")