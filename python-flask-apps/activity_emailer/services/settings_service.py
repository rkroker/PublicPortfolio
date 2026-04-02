"""
Author: Ryan Kroker (ryan.kroker@gmail.com)
Version: 1.0
Created: 3-30-2026
Last Updated: 4-2-2026
Purpose: Handles loading, storing, and formatting configurable email and safeguard settings.
"""

from models import AppSettings, db

DEFAULT_EMAIL_SUBJECT = "Academic Eligibility Notice"

DEFAULT_EMAIL_BODY = """Hello {{ student_name }},

Our records indicate that you are currently earning one or more failing grades, which makes you ineligible to participate in after school activities at this time.

Failing courses:
{{ failing_courses }}

Current activities:
{{ activities }}

Please work with your teacher or teachers to address these academic deficiencies before returning to participation.

Your activity advisor or advisors and the teacher or teachers connected to your current failing grades have been copied on this message so everyone has the same information.

Thank you."""


def get_or_create_settings():
    settings = AppSettings.query.first()

    if not settings:
        settings = AppSettings(
            mail_server="smtp.gmail.com",
            mail_port=587,
            mail_use_tls=True,
            mail_username="",
            mail_password="",
            mail_from="",
            test_email_recipient="",
            live_send_password="SEND LIVE",
            default_email_subject="Academic Eligibility Notice",
            default_email_body=DEFAULT_EMAIL_BODY,
            email_test_status="not_tested",
            email_tested_at=None,
            email_test_recipient="",
            email_test_message="Email settings have not been tested yet.",
        )
        db.session.add(settings)
        db.session.commit()

    if not settings.default_email_body:
        settings.default_email_body = DEFAULT_EMAIL_BODY
        db.session.commit()

    if not settings.default_email_subject:
        settings.default_email_subject = DEFAULT_EMAIL_SUBJECT
        db.session.commit()

    if not settings.live_send_password:
        settings.live_send_password = "SEND LIVE"
        db.session.commit()

    if not settings.email_test_status:
        settings.email_test_status = "not_tested"
        settings.email_test_message = "Email settings have not been tested yet."
        db.session.commit()

    return settings


def format_failing_courses(failing_courses):
    lines = []
    for course in failing_courses:
        lines.append(f"- {course['course_name']}: {course['current_grade']}")
    return "\n".join(lines)


def format_activities(activities):
    return "\n".join([f"- {activity}" for activity in activities])


def render_template_text(template_text, context):
    rendered = template_text

    for key, value in context.items():
        rendered = rendered.replace(f"{{{{ {key} }}}}", value)

    return rendered