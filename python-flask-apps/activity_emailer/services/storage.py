"""
Author: Ryan Kroker (ryan.kroker@gmail.com)
Version: 1.0
Created: 3-30-2026
Last Updated: 4-2-2026
Purpose: Stores finalized runs and their notification records in the database.
"""

import json

from models import Notification, Run, db


def save_run_with_notifications(notifications):
    run = Run(
        status="finalized",
        send_mode="none",
        total_notifications=len(notifications),
    )
    db.session.add(run)
    db.session.flush()

    for item in notifications:
        notification = Notification(
            run_id=run.id,
            notification_type=item["notification_type"],
            recipient_type=item["recipient_type"],
            to_email=item["to_email"],
            cc_emails=json.dumps(item.get("cc_emails", [])),
            recipient_name=item["recipient_name"],
            recipient_identifier=item.get("recipient_identifier"),
            student_id=item.get("student_id"),
            student_name=item.get("student_name"),
            activity_names_json=json.dumps(item.get("activity_names", [])),
            failing_courses_json=json.dumps(item.get("failing_courses", [])),
            related_students_json=json.dumps(item.get("related_students", [])),
            subject=item["subject"],
            body=item["body"],
            send_status="pending",
            send_mode="none",
        )
        db.session.add(notification)

    db.session.commit()
    return run