"""
Author: Ryan Kroker (ryan.kroker@gmail.com)
Version: 1.0
Created: 3-23-2026
Last Updated: 4-2-2026
Purpose: Validates uploaded files for the required column structure before business rule checks run.
"""

REQUIRED_COLUMNS = {
    "student_activity": {
        "student_id",
        "student_name",
        "student_email",
        "activity_name",
    },
    "staff_activity": {
        "activity_name",
        "advisor_name",
        "advisor_email",
    },
    "current_grades": {
        "student_id",
        "student_name",
        "course_name",
        "current_grade",
        "teacher_name",
        "teacher_email",
    },
}


def validate_required_columns(df, file_type):
    required = REQUIRED_COLUMNS[file_type]
    actual = set(df.columns)
    missing = required - actual
    return sorted(list(missing))