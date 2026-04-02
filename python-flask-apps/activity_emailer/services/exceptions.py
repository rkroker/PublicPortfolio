"""
Author: Ryan Kroker (ryan.kroker@gmail.com)
Version: 1.0
Created: 3-23-2026
Last Updated: 4-2-2026
Purpose: Stores validation and processing exceptions in the database for run auditing.
"""

from models import ExceptionLog, db


def save_exceptions(run_id, exceptions):
    for item in exceptions:
        exception = ExceptionLog(
            run_id=run_id,
            issue_type=item["issue_type"],
            record_type=item["record_type"],
            record_key=item.get("record_key"),
            details=item["details"],
        )
        db.session.add(exception)

    db.session.commit()