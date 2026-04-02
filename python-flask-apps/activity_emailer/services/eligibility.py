"""
Author: Ryan Kroker (ryan.kroker@gmail.com)
Version: 1.0
Created: 3-30-2026
Last Updated: 4-2-2026
Purpose: Builds eligibility results and notification data from validated student, staff, and grade inputs.
"""

from services.settings_service import (
    format_activities,
    format_failing_courses,
    get_or_create_settings,
    render_template_text,
)


def clean_text(value):
    if value is None:
        return ""

    text = str(value).strip()

    if text.lower() == "nan":
        return ""

    return text


def is_failing_grade(value):
    text = clean_text(value)

    if text == "":
        return False

    if text.upper() == "INC":
        return False

    try:
        return float(text) <= 65
    except ValueError:
        return False


def build_notifications(student_activity_df, staff_activity_df, current_grades_df):
    settings = get_or_create_settings()
    notifications = []

    student_activity_df = student_activity_df.copy()
    staff_activity_df = staff_activity_df.copy()
    current_grades_df = current_grades_df.copy()

    student_activity_df["student_id"] = student_activity_df["student_id"].apply(clean_text)
    student_activity_df["student_name"] = student_activity_df["student_name"].apply(clean_text)
    student_activity_df["student_email"] = student_activity_df["student_email"].apply(clean_text)
    student_activity_df["activity_name"] = student_activity_df["activity_name"].apply(clean_text)

    staff_activity_df["activity_name"] = staff_activity_df["activity_name"].apply(clean_text)
    staff_activity_df["advisor_name"] = staff_activity_df["advisor_name"].apply(clean_text)
    staff_activity_df["advisor_email"] = staff_activity_df["advisor_email"].apply(clean_text)

    current_grades_df["student_id"] = current_grades_df["student_id"].apply(clean_text)
    current_grades_df["student_name"] = current_grades_df["student_name"].apply(clean_text)
    current_grades_df["course_name"] = current_grades_df["course_name"].apply(clean_text)
    current_grades_df["current_grade"] = current_grades_df["current_grade"].apply(clean_text)
    current_grades_df["teacher_name"] = current_grades_df["teacher_name"].apply(clean_text)
    current_grades_df["teacher_email"] = current_grades_df["teacher_email"].apply(clean_text)

    student_activities = {}
    student_info = {}

    for _, row in student_activity_df.iterrows():
        student_id = row["student_id"]
        activity_name = row["activity_name"]

        if not student_id or not activity_name:
            continue

        student_activities.setdefault(student_id, set()).add(activity_name)
        student_info[student_id] = {
            "student_name": row["student_name"],
            "student_email": row["student_email"],
        }

    activity_advisors = {}

    for _, row in staff_activity_df.iterrows():
        activity_name = row["activity_name"]
        advisor_email = row["advisor_email"]

        if not activity_name or not advisor_email:
            continue

        activity_advisors.setdefault(activity_name, set()).add(advisor_email)

    current_grades_df["is_failing"] = current_grades_df["current_grade"].apply(is_failing_grade)
    failing_grades_df = current_grades_df[current_grades_df["is_failing"]].copy()

    failing_by_student = {}

    for _, row in failing_grades_df.iterrows():
        student_id = row["student_id"]

        if student_id not in student_activities:
            continue

        failing_by_student.setdefault(student_id, []).append({
            "course_name": row["course_name"],
            "current_grade": row["current_grade"],
            "teacher_name": row["teacher_name"],
            "teacher_email": row["teacher_email"],
        })

    for student_id, failing_courses in failing_by_student.items():
        if student_id not in student_info:
            continue

        student_name = student_info[student_id]["student_name"]
        student_email = student_info[student_id]["student_email"]
        activities = sorted(student_activities.get(student_id, set()))

        teacher_emails = sorted({
            course["teacher_email"]
            for course in failing_courses
            if course["teacher_email"]
        })

        advisor_emails = sorted({
            email
            for activity in activities
            for email in activity_advisors.get(activity, set())
        })

        cc_emails = sorted(set(teacher_emails + advisor_emails))

        context = {
            "student_name": student_name,
            "failing_courses": format_failing_courses(failing_courses),
            "activities": format_activities(activities),
        }

        subject = render_template_text(settings.default_email_subject, context)
        body = render_template_text(settings.default_email_body, context)

        notifications.append({
            "notification_type": "thread",
            "recipient_type": "student",
            "to_email": student_email,
            "cc_emails": cc_emails,
            "recipient_name": student_name,
            "recipient_identifier": student_id,
            "student_id": student_id,
            "student_name": student_name,
            "activity_names": activities,
            "failing_courses": failing_courses,
            "related_students": [],
            "subject": subject,
            "body": body,
        })

    return sorted(notifications, key=lambda x: x["recipient_name"])