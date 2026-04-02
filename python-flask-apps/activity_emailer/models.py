"""
Author: Ryan Kroker (ryan.kroker@gmail.com)
Version: 1.0
Created: 3-30-2026
Last Updated: 4-2-2026
Purpose: Defines the database models and relationships used by runs, notifications, exceptions, and settings.
"""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Run(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(50), default="finalized", nullable=False)
    send_mode = db.Column(db.String(20), default="none", nullable=False)

    total_students_in_activities = db.Column(db.Integer, default=0)
    total_students_failing = db.Column(db.Integer, default=0)
    total_notifications = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)

    notifications = db.relationship("Notification", backref="run", lazy=True, cascade="all, delete-orphan")
    exceptions = db.relationship("ExceptionLog", backref="run", lazy=True, cascade="all, delete-orphan")


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey("run.id"), nullable=False)

    notification_type = db.Column(db.String(50), nullable=False)
    recipient_type = db.Column(db.String(50), nullable=False)

    to_email = db.Column(db.String(255), nullable=False)
    cc_emails = db.Column(db.Text)

    recipient_name = db.Column(db.String(255), nullable=False)
    recipient_identifier = db.Column(db.String(255))

    student_id = db.Column(db.String(50))
    student_name = db.Column(db.String(255))

    activity_names_json = db.Column(db.Text)
    failing_courses_json = db.Column(db.Text)
    related_students_json = db.Column(db.Text)

    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)

    send_status = db.Column(db.String(50), default="pending", nullable=False)
    send_mode = db.Column(db.String(20), default="none", nullable=False)

    error_message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime)


class ExceptionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey("run.id"), nullable=False)
    issue_type = db.Column(db.String(100), nullable=False)
    record_type = db.Column(db.String(100), nullable=False)
    record_key = db.Column(db.String(255))
    details = db.Column(db.Text, nullable=False)


class AppSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    mail_server = db.Column(db.String(255), nullable=False, default="smtp.gmail.com")
    mail_port = db.Column(db.Integer, nullable=False, default=587)
    mail_use_tls = db.Column(db.Boolean, nullable=False, default=True)
    mail_username = db.Column(db.String(255), default="")
    mail_password = db.Column(db.Text, default="")
    mail_from = db.Column(db.String(255), default="")
    test_email_recipient = db.Column(db.String(255), default="")

    live_send_password = db.Column(db.String(255), nullable=False, default="SEND LIVE")

    default_email_subject = db.Column(db.String(255), nullable=False, default="Academic Eligibility Notice")
    default_email_body = db.Column(db.Text, nullable=False, default="")

    email_test_status = db.Column(db.String(50), nullable=False, default="not_tested")
    email_tested_at = db.Column(db.DateTime)
    email_test_recipient = db.Column(db.String(255), default="")
    email_test_message = db.Column(db.Text, default="")