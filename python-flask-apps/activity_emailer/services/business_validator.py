"""
Author: Ryan Kroker (ryan.kroker@gmail.com)
Version: 1.0
Created: 3-25-2026
Last Updated: 4-2-2026
Purpose: Handles business rule validation for uploaded activity, roster, and grade data.
"""

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


def validate_business_rules(student_activity_df, staff_activity_df, current_grades_df):
    blocking_issues = []
    warnings = []

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
    all_staff_activities = set()

    for _, row in staff_activity_df.iterrows():
        activity_name = row["activity_name"]

        if not activity_name:
            continue

        all_staff_activities.add(activity_name)
        activity_advisors.setdefault(activity_name, []).append({
            "advisor_name": row["advisor_name"],
            "advisor_email": row["advisor_email"],
        })

    current_grades_df["is_failing"] = current_grades_df["current_grade"].apply(is_failing_grade)
    failing_grades_df = current_grades_df[current_grades_df["is_failing"]].copy()

    failing_students = set(failing_grades_df["student_id"].tolist())
    activity_students = set(student_activities.keys())
    qualifying_students = failing_students.intersection(activity_students)

    used_activities = set()

    for student_id in sorted(qualifying_students):
        student_name = student_info.get(student_id, {}).get("student_name", "")
        student_email = student_info.get(student_id, {}).get("student_email", "")
        activities = sorted(student_activities.get(student_id, set()))

        if not student_email:
            blocking_issues.append({
                "issue_type": "missing_student_email",
                "record_type": "student",
                "record_key": student_id,
                "details": f"Student {student_name} ({student_id}) qualifies for notification but has no student email.",
            })

        student_failing_courses = failing_grades_df[failing_grades_df["student_id"] == student_id]

        for _, course_row in student_failing_courses.iterrows():
            course_name = course_row["course_name"]
            teacher_email = course_row["teacher_email"]

            if not teacher_email:
                blocking_issues.append({
                    "issue_type": "missing_teacher_email",
                    "record_type": "course",
                    "record_key": f"{student_id}:{course_name}",
                    "details": (
                        f"Failing course {course_name} for student "
                        f"{student_name} ({student_id}) is missing a teacher email."
                    ),
                })

            elif not course_row["teacher_name"]:
                warnings.append({
                    "issue_type": "missing_teacher_name",
                    "record_type": "course",
                    "record_key": f"{student_id}:{course_name}",
                    "details": (
                        f"Failing course {course_name} for student "
                        f"{student_name} ({student_id}) has a teacher email but no teacher name."
                    ),
                })

        for activity in activities:
            used_activities.add(activity)
            advisors = activity_advisors.get(activity, [])

            if not advisors:
                blocking_issues.append({
                    "issue_type": "missing_activity_advisor_match",
                    "record_type": "activity",
                    "record_key": activity,
                    "details": (
                        f"Activity {activity} for student {student_name} ({student_id}) "
                        "has no matching advisor record in the staff activity file."
                    ),
                })
                continue

            advisor_emails = [advisor["advisor_email"] for advisor in advisors if advisor["advisor_email"]]

            if not advisor_emails:
                blocking_issues.append({
                    "issue_type": "missing_advisor_email",
                    "record_type": "activity",
                    "record_key": activity,
                    "details": (
                        f"Activity {activity} for student {student_name} ({student_id}) "
                        "has advisor record(s) but no advisor email."
                    ),
                })

            for advisor in advisors:
                if advisor["advisor_email"] and not advisor["advisor_name"]:
                    warnings.append({
                        "issue_type": "missing_advisor_name",
                        "record_type": "activity",
                        "record_key": activity,
                        "details": (
                            f"Activity {activity} has an advisor email but no advisor name."
                        ),
                    })

    failing_without_activity = failing_students - activity_students
    for student_id in sorted(failing_without_activity):
        matching_rows = failing_grades_df[failing_grades_df["student_id"] == student_id]
        student_name = ""
        if not matching_rows.empty:
            student_name = clean_text(matching_rows.iloc[0]["student_name"])

        warnings.append({
            "issue_type": "failing_student_not_in_activity",
            "record_type": "student",
            "record_key": student_id,
            "details": f"Student {student_name} ({student_id}) is failing but is not in any activity.",
        })

    for activity in sorted(all_staff_activities - used_activities):
        warnings.append({
            "issue_type": "unused_staff_activity",
            "record_type": "activity",
            "record_key": activity,
            "details": f"Activity {activity} exists in the staff file but was not used by any qualifying student.",
        })

    return {
        "blocking_issues": blocking_issues,
        "warnings": warnings,
        "qualifying_student_count": len(qualifying_students),
        "can_finalize": len(blocking_issues) == 0,
    }