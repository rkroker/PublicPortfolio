"""
Author: Ryan Kroker (ryan.kroker@gmail.com)
Version: 1.0
Created: 3-30-2026
Last Updated: 4-2-2026
Purpose: Defines the Flask-WTF forms used for uploads, send actions, and application settings.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import BooleanField, IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Optional


class UploadFilesForm(FlaskForm):
    student_activity_file = FileField("Student Activity File", validators=[FileRequired()])
    staff_activity_file = FileField("Staff Activity File", validators=[FileRequired()])
    current_grades_file = FileField("Current Grades File", validators=[FileRequired()])
    submit = SubmitField("Upload and Validate")


class FinalizeRunForm(FlaskForm):
    submit = SubmitField("Finalize Run")


class SendRunForm(FlaskForm):
    submit = SubmitField("Send Run in Test Mode")


class LiveSendForm(FlaskForm):
    confirmation_text = StringField("Type SEND LIVE to confirm", validators=[DataRequired()])
    submit = SubmitField("Send Run Live")


class EmailSettingsForm(FlaskForm):
    mail_server = StringField("Mail Server", validators=[DataRequired()])
    mail_port = IntegerField("Mail Port", validators=[DataRequired(), NumberRange(min=1, max=65535)])
    mail_use_tls = BooleanField("Use TLS")
    mail_username = StringField("Mail Username", validators=[Optional()])
    mail_password = StringField("Mail Password", validators=[Optional()])
    mail_from = StringField("Mail From", validators=[Optional()])
    test_email_recipient = StringField("Test Email Recipient", validators=[Optional()])
    submit_email = SubmitField("Save Email Settings")
    test_email = SubmitField("Test Email Settings")


class SafeguardSettingsForm(FlaskForm):
    live_send_password = StringField("Live Send Passcode", validators=[DataRequired()])
    submit_safeguard = SubmitField("Save Safeguard Settings")


class TemplateSettingsForm(FlaskForm):
    default_email_subject = StringField("Default Email Subject", validators=[DataRequired()])
    default_email_body = TextAreaField("Default Email Body", validators=[DataRequired()])
    submit_template = SubmitField("Save Template Settings")
    reset_template = SubmitField("Reset Template to Default")