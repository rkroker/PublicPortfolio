"""
Author: Ryan Kroker (ryan.kroker@gmail.com)
Version: 1.0
Created: 3-30-2026
Last Updated: 4-2-2026
Purpose: Handles the web routes for uploads, validation, previews, exports, email sending, and settings.
"""

import json
import csv
import io

from pathlib import Path
from uuid import uuid4
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from models import Notification, Run, db
from sqlalchemy import cast, or_
from flask import (
    Blueprint, 
    current_app, 
    flash, 
    redirect, 
    render_template, 
    request, 
    session, 
    url_for, 
    Response)
from forms import (
    EmailSettingsForm,
    FinalizeRunForm,
    LiveSendForm,
    SafeguardSettingsForm,
    SendRunForm,
    TemplateSettingsForm,
    UploadFilesForm,
)

from services.business_validator import validate_business_rules
from services.eligibility import build_notifications
from services.file_parser import load_csv_file, normalize_columns
from services.storage import save_run_with_notifications
from services.validator import validate_required_columns
from services.settings_service import (
    DEFAULT_EMAIL_BODY,
    DEFAULT_EMAIL_SUBJECT,
    get_or_create_settings,
)
from services.email_service import (
    build_live_message,
    build_settings_test_message,
    build_test_mode_message,
    send_email_message,
)

main = Blueprint("main", __name__)


def save_uploaded_file(file_storage, prefix):
    original_name = secure_filename(file_storage.filename)
    unique_name = f"{prefix}_{uuid4().hex}_{original_name}"
    save_path = Path(current_app.config["UPLOAD_FOLDER"]) / unique_name
    file_storage.save(save_path)
    return unique_name, save_path

def update_run_send_status(run, mode):
    notification_statuses = [notification.send_status for notification in run.notifications]

    if not notification_statuses:
        run.status = "finalized"
        run.send_mode = "none"
        return

    if mode == "test":
        if all(status == "sent_test" for status in notification_statuses):
            run.status = "sent_test"
            run.send_mode = "test"
        elif any(status == "sent_test" for status in notification_statuses):
            run.status = "partially_sent_test"
            run.send_mode = "test"
        elif any(status == "failed_test" for status in notification_statuses):
            run.status = "failed_test"
            run.send_mode = "test"
        else:
            run.status = "finalized"
            run.send_mode = "none"

    elif mode == "live":
        live_statuses = [status for status in notification_statuses if status in ("sent_live", "failed_live")]

        if not live_statuses:
            return

        if all(status == "sent_live" for status in live_statuses):
            run.status = "sent_live"
            run.send_mode = "live"
        elif any(status == "sent_live" for status in live_statuses):
            run.status = "partially_sent_live"
            run.send_mode = "live"
        elif any(status == "failed_live" for status in live_statuses):
            run.status = "failed_live"
            run.send_mode = "live"

@main.route("/")
def index():
    return render_template("index.html")


@main.route("/upload", methods=["GET", "POST"])
def upload():
    form = UploadFilesForm()
    finalize_form = FinalizeRunForm()

    if form.validate_on_submit():
        student_file = form.student_activity_file.data
        staff_file = form.staff_activity_file.data
        grades_file = form.current_grades_file.data

        saved_files = {}
        saved_paths = {}

        file_map = [
            ("student_activity_file", student_file, "student_activity"),
            ("staff_activity_file", staff_file, "staff_activity"),
            ("current_grades_file", grades_file, "current_grades"),
        ]

        for field_name, file_obj, prefix in file_map:
            saved_name, saved_path = save_uploaded_file(file_obj, prefix)
            saved_files[field_name] = saved_name
            saved_paths[prefix] = str(saved_path)

        structure_results = {}
        has_structure_errors = False
        loaded_dataframes = {}

        for file_type, path in saved_paths.items():
            try:
                df = load_csv_file(path)
                df = normalize_columns(df)
                missing_columns = validate_required_columns(df, file_type)

                is_empty = len(df) == 0

                structure_results[file_type] = {
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "missing_columns": missing_columns,
                    "is_empty": is_empty,
                    "valid": len(missing_columns) == 0 and not is_empty,
                    "error": None,
                }

                if missing_columns or is_empty:
                    has_structure_errors = True
                else:
                    loaded_dataframes[file_type] = df

            except Exception as e:
                structure_results[file_type] = {
                    "row_count": 0,
                    "column_count": 0,
                    "missing_columns": [],
                    "is_empty": False,
                    "valid": False,
                    "error": str(e),
                }
                has_structure_errors = True

        business_results = None

        session.pop("validated_upload", None)

        if has_structure_errors:
            flash("Upload completed, but structure validation failed. Correct the files and reupload.", "error")
        else:
            business_results = validate_business_rules(
                loaded_dataframes["student_activity"],
                loaded_dataframes["staff_activity"],
                loaded_dataframes["current_grades"],
            )

            if business_results["can_finalize"]:
                session["validated_upload"] = {
                    "saved_files": saved_files,
                    "saved_paths": saved_paths,
                }
                flash("Validation passed. This upload is ready to finalize.", "success")
            else:
                flash("Validation found blocking issues. Correct the files and reupload.", "error")

        return render_template(
            "review.html",
            uploaded_files=saved_files,
            structure_results=structure_results,
            business_results=business_results,
            finalize_form=finalize_form,
        )

    if request.method == "POST":
        flash("Please upload all three required files.", "error")

    return render_template(
        "upload.html",
        form=form,
    )


@main.route("/finalize", methods=["POST"])
def finalize():
    finalize_form = FinalizeRunForm()

    if not finalize_form.validate_on_submit():
        flash("Unable to finalize the run.", "error")
        return redirect(url_for("main.upload"))

    validated_upload = session.get("validated_upload")

    if not validated_upload:
        flash("No validated upload was found. Please upload and validate files first.", "error")
        return redirect(url_for("main.upload"))

    saved_paths = validated_upload["saved_paths"]

    try:
        student_activity_df = normalize_columns(load_csv_file(saved_paths["student_activity"]))
        staff_activity_df = normalize_columns(load_csv_file(saved_paths["staff_activity"]))
        current_grades_df = normalize_columns(load_csv_file(saved_paths["current_grades"]))

        business_results = validate_business_rules(
            student_activity_df,
            staff_activity_df,
            current_grades_df,
        )

        if not business_results["can_finalize"]:
            session.pop("validated_upload", None)
            flash("The validated upload is no longer eligible to finalize. Please reupload and validate again.", "error")
            return redirect(url_for("main.upload"))

        notifications = build_notifications(
            student_activity_df,
            staff_activity_df,
            current_grades_df,
        )

        saved_run = save_run_with_notifications(notifications)

        session.pop("validated_upload", None)

        flash("Run finalized and saved successfully.", "success")
        return redirect(url_for("main.run_detail", run_id=saved_run.id))

    except Exception as e:
        flash(f"An error occurred while finalizing the run: {e}", "error")
        return redirect(url_for("main.upload"))


@main.route("/review")
def review():
    return render_template(
        "review.html",
        uploaded_files=None,
        structure_results=None,
        business_results=None,
        finalize_form=FinalizeRunForm(),
    )


@main.route("/history")
def history():
    q = (request.args.get("q") or "").strip()
    status_filter = (request.args.get("status") or "").strip()
    send_mode_filter = (request.args.get("send_mode") or "").strip()
    date_from = (request.args.get("date_from") or "").strip()
    date_to = (request.args.get("date_to") or "").strip()
    has_exceptions = (request.args.get("has_exceptions") or "").strip()

    query = Run.query

    if status_filter:
        query = query.filter(Run.status == status_filter)

    if send_mode_filter:
        query = query.filter(Run.send_mode == send_mode_filter)

    if q:
        like_value = f"%{q}%"
        query = query.filter(
            or_(
                cast(Run.id, db.String).ilike(like_value),
                Run.status.ilike(like_value),
                Run.send_mode.ilike(like_value),
            )
        )

    if date_from:
        try:
            from_dt = datetime.strptime(date_from, "%Y-%m-%d")
            query = query.filter(Run.created_at >= from_dt)
        except ValueError:
            flash("Invalid From date.", "error")

    if date_to:
        try:
            to_dt = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(Run.created_at < to_dt)
        except ValueError:
            flash("Invalid To date.", "error")

    if has_exceptions == "yes":
        query = query.filter(Run.exceptions.any())
    elif has_exceptions == "no":
        query = query.filter(~Run.exceptions.any())

    runs = query.order_by(Run.created_at.desc()).all()

    history_rows = []
    for run in runs:
        history_rows.append({
            "id": run.id,
            "created_at": run.created_at,
            "status": run.status,
            "send_mode": run.send_mode,
            "total_notifications": run.total_notifications,
            "total_exceptions": len(run.exceptions),
        })

    status_options = [
        "",
        "finalized",
        "sent_test",
        "failed_test",
        "partially_sent_test",
        "sent_live",
        "failed_live",
        "partially_sent_live",
    ]

    send_mode_options = ["", "none", "test", "live"]
    has_exceptions_options = ["", "yes", "no"]

    return render_template(
        "history.html",
        runs=history_rows,
        q=q,
        status_filter=status_filter,
        send_mode_filter=send_mode_filter,
        date_from=date_from,
        date_to=date_to,
        has_exceptions=has_exceptions,
        status_options=status_options,
        send_mode_options=send_mode_options,
        has_exceptions_options=has_exceptions_options,
    )


@main.route("/history/<int:run_id>")
def run_detail(run_id):
    run = Run.query.get_or_404(run_id)

    notifications = []
    for item in run.notifications:
        notifications.append({
            "notification_type": item.notification_type,
            "recipient_type": item.recipient_type,
            "to_email": item.to_email,
            "cc_emails": json.loads(item.cc_emails or "[]"),
            "recipient_name": item.recipient_name,
            "recipient_identifier": item.recipient_identifier,
            "student_id": item.student_id,
            "student_name": item.student_name,
            "activity_names": json.loads(item.activity_names_json or "[]"),
            "failing_courses": json.loads(item.failing_courses_json or "[]"),
            "related_students": json.loads(item.related_students_json or "[]"),
            "send_status": item.send_status,
            "send_mode": item.send_mode,
        })

    unique_students = set()
    unique_activities = set()
    unique_teacher_emails = set()
    unique_advisor_emails = set()
    total_failing_courses = 0
    activity_student_counts = {}
    notification_type_counts = {}

    for notification in notifications:
        notification_type = notification["notification_type"]
        notification_type_counts[notification_type] = notification_type_counts.get(notification_type, 0) + 1

        if notification["student_id"]:
            unique_students.add(notification["student_id"])

        total_failing_courses += len(notification["failing_courses"])

        for activity in notification["activity_names"]:
            unique_activities.add(activity)
            activity_student_counts[activity] = activity_student_counts.get(activity, 0) + 1

        for course in notification["failing_courses"]:
            teacher_email = course.get("teacher_email")
            if teacher_email:
                unique_teacher_emails.add(teacher_email)

        for cc_email in notification["cc_emails"]:
            if cc_email and cc_email not in unique_teacher_emails:
                unique_advisor_emails.add(cc_email)

    summary = {
        "unique_students": len(unique_students),
        "unique_activities": len(unique_activities),
        "unique_teacher_emails": len(unique_teacher_emails),
        "unique_advisor_emails": len(unique_advisor_emails),
        "total_failing_courses": total_failing_courses,
        "activity_student_counts": dict(sorted(activity_student_counts.items())),
        "notification_type_counts": dict(sorted(notification_type_counts.items())),
    }

    exceptions = []
    for item in run.exceptions:
        exceptions.append({
            "issue_type": item.issue_type,
            "record_type": item.record_type,
            "record_key": item.record_key,
            "details": item.details,
        })

    return render_template(
        "run_detail.html",
        run=run,
        summary=summary,
        exceptions=exceptions,
    )

@main.route("/history/<int:run_id>/preview")
def run_preview(run_id):
    run = Run.query.get_or_404(run_id)

    notifications = []
    for item in run.notifications:
        notifications.append({
            "id": item.id,
            "notification_type": item.notification_type,
            "recipient_type": item.recipient_type,
            "to_email": item.to_email,
            "cc_emails": json.loads(item.cc_emails or "[]"),
            "recipient_name": item.recipient_name,
            "recipient_identifier": item.recipient_identifier,
            "student_id": item.student_id,
            "student_name": item.student_name,
            "activity_names": json.loads(item.activity_names_json or "[]"),
            "failing_courses": json.loads(item.failing_courses_json or "[]"),
            "related_students": json.loads(item.related_students_json or "[]"),
            "subject": item.subject,
            "body": item.body,
            "send_status": item.send_status,
            "send_mode": item.send_mode,
            "sent_at": item.sent_at,
            "error_message": item.error_message,
        })

    pending_count = sum(1 for n in notifications if n["send_status"] == "pending")
    failed_test_count = sum(1 for n in notifications if n["send_status"] == "failed_test")
    sent_live_count = sum(1 for n in notifications if n["send_status"] == "sent_live")

    return render_template(
        "run_preview.html",
        run=run,
        notifications=notifications,
        pending_count=pending_count,
        failed_test_count=failed_test_count,
        sent_live_count=sent_live_count,
        send_form=SendRunForm(),
        live_form=LiveSendForm(),
    )

@main.route("/history/<int:run_id>/send-test", methods=["POST"])
def send_test_run(run_id):
    run = Run.query.get_or_404(run_id)
    send_form = SendRunForm()

    if not send_form.validate_on_submit():
        flash("Unable to submit test send.", "error")
        return redirect(url_for("main.run_preview", run_id=run.id))

    settings = get_or_create_settings()
    test_recipient = settings.test_email_recipient
    mail_from = settings.mail_from

    if not test_recipient or not mail_from:
        flash("Test email configuration is incomplete. Set MAIL_FROM and TEST_EMAIL_RECIPIENT.", "error")
        return redirect(url_for("main.run_preview", run_id=run.id))

    pending_notifications = Notification.query.filter_by(run_id=run.id, send_status="pending").all()

    if not pending_notifications:
        flash("There are no pending notifications to send for this run.", "error")
        return redirect(url_for("main.run_preview", run_id=run.id))

    sent_count = 0
    failed_count = 0

    for notification in pending_notifications:
        try:
            notification.cc_emails_list = json.loads(notification.cc_emails or "[]")
            message = build_test_mode_message(notification)
            send_email_message(message)

            notification.send_status = "sent_test"
            notification.send_mode = "test"
            notification.error_message = None
            notification.sent_at = datetime.utcnow()
            sent_count += 1

        except Exception as e:
            notification.send_status = "failed_test"
            notification.send_mode = "test"
            notification.error_message = str(e)
            failed_count += 1

    update_run_send_status(run, "test")
    db.session.commit()

    flash(
        f"Test send complete. Sent: {sent_count}. Failed: {failed_count}.",
        "success" if failed_count == 0 else "error",
    )
    return redirect(url_for("main.run_preview", run_id=run.id))

@main.route("/history/<int:run_id>/retry-test", methods=["POST"])
def retry_failed_test_run(run_id):
    run = Run.query.get_or_404(run_id)
    send_form = SendRunForm()

    if not send_form.validate_on_submit():
        flash("Unable to submit retry test send.", "error")
        return redirect(url_for("main.run_preview", run_id=run.id))

    settings = get_or_create_settings()
    test_recipient = settings.test_email_recipient
    mail_from = settings.mail_from

    if not test_recipient or not mail_from:
        flash("Test email configuration is incomplete. Set MAIL_FROM and TEST_EMAIL_RECIPIENT.", "error")
        return redirect(url_for("main.run_preview", run_id=run.id))

    failed_notifications = Notification.query.filter_by(run_id=run.id, send_status="failed_test").all()

    if not failed_notifications:
        flash("There are no failed test notifications to retry for this run.", "error")
        return redirect(url_for("main.run_preview", run_id=run.id))

    sent_count = 0
    failed_count = 0

    for notification in failed_notifications:
        try:
            notification.cc_emails_list = json.loads(notification.cc_emails or "[]")
            message = build_test_mode_message(notification)
            send_email_message(message)

            notification.send_status = "sent_test"
            notification.send_mode = "test"
            notification.error_message = None
            notification.sent_at = datetime.utcnow()
            sent_count += 1

        except Exception as e:
            notification.send_status = "failed_test"
            notification.send_mode = "test"
            notification.error_message = str(e)
            failed_count += 1

    update_run_send_status(run, "test")
    db.session.commit()

    flash(
        f"Retry test send complete. Sent: {sent_count}. Failed: {failed_count}.",
        "success" if failed_count == 0 else "error",
    )
    return redirect(url_for("main.run_preview", run_id=run.id))

@main.route("/history/<int:run_id>/send-live", methods=["POST"])
def send_live_run(run_id):
    run = Run.query.get_or_404(run_id)
    live_form = LiveSendForm()

    if not live_form.validate_on_submit():
        flash("Unable to submit live send.", "error")
        return redirect(url_for("main.run_preview", run_id=run.id))

    settings = get_or_create_settings()

    if live_form.confirmation_text.data.strip() != settings.live_send_password:
        flash("Live send confirmation failed. Enter the correct confirmation value.", "error")
        return redirect(url_for("main.run_preview", run_id=run.id))

    
    mail_from = settings.mail_from

    if not mail_from:
        flash("Live email configuration is incomplete. Set MAIL_FROM.", "error")
        return redirect(url_for("main.run_preview", run_id=run.id))

    already_live_sent = Notification.query.filter_by(run_id=run.id, send_status="sent_live").count()
    if already_live_sent > 0:
        flash("This run has already been live-sent in full or in part. Live resend is blocked in this version.", "error")
        return redirect(url_for("main.run_preview", run_id=run.id))

    eligible_notifications = Notification.query.filter(
        Notification.run_id == run.id,
        Notification.send_status.in_(["pending", "sent_test", "failed_test"])
    ).all()

    if not eligible_notifications:
        flash("There are no eligible notifications available for live send.", "error")
        return redirect(url_for("main.run_preview", run_id=run.id))

    sent_count = 0
    failed_count = 0

    for notification in eligible_notifications:
        try:
            notification.cc_emails_list = json.loads(notification.cc_emails or "[]")
            message = build_live_message(notification)
            send_email_message(message)

            notification.send_status = "sent_live"
            notification.send_mode = "live"
            notification.error_message = None
            notification.sent_at = datetime.utcnow()
            sent_count += 1

        except Exception as e:
            notification.send_status = "failed_live"
            notification.send_mode = "live"
            notification.error_message = str(e)
            failed_count += 1

    update_run_send_status(run, "live")
    db.session.commit()

    flash(
        f"Live send complete. Sent: {sent_count}. Failed: {failed_count}.",
        "success" if failed_count == 0 else "error",
    )
    return redirect(url_for("main.run_preview", run_id=run.id))

@main.route("/settings", methods=["GET", "POST"])
def settings():
    settings = get_or_create_settings()

    email_form = EmailSettingsForm(prefix="email")
    safeguard_form = SafeguardSettingsForm(prefix="safeguard")
    template_form = TemplateSettingsForm(prefix="template")

    active_tab = request.args.get("tab", "email")

    if request.method == "GET":
        email_form.mail_server.data = settings.mail_server
        email_form.mail_port.data = settings.mail_port
        email_form.mail_use_tls.data = settings.mail_use_tls
        email_form.mail_username.data = settings.mail_username
        email_form.mail_password.data = settings.mail_password
        email_form.mail_from.data = settings.mail_from
        email_form.test_email_recipient.data = settings.test_email_recipient

        safeguard_form.live_send_password.data = settings.live_send_password

        template_form.default_email_subject.data = settings.default_email_subject
        template_form.default_email_body.data = settings.default_email_body

    if (email_form.submit_email.data or email_form.test_email.data) and email_form.validate_on_submit():
        settings.mail_server = email_form.mail_server.data.strip()
        settings.mail_port = email_form.mail_port.data
        settings.mail_use_tls = email_form.mail_use_tls.data
        settings.mail_username = (email_form.mail_username.data or "").strip()
        settings.mail_password = (email_form.mail_password.data or "").strip()
        settings.mail_from = (email_form.mail_from.data or "").strip()
        settings.test_email_recipient = (email_form.test_email_recipient.data or "").strip()

        if email_form.submit_email.data:
            settings.email_test_status = "not_tested"
            settings.email_tested_at = None
            settings.email_test_recipient = ""
            settings.email_test_message = "Email settings were updated and should be tested again."

            db.session.commit()
            flash("Email settings saved successfully.", "success")
            return redirect(url_for("main.settings", tab="email"))

        if email_form.test_email.data:
            if not settings.mail_from or not settings.test_email_recipient:
                settings.email_test_status = "failed"
                settings.email_tested_at = datetime.utcnow()
                settings.email_test_recipient = settings.test_email_recipient
                settings.email_test_message = "Mail From and Test Email Recipient are required to send a test email."
                db.session.commit()

                flash("Mail From and Test Email Recipient are required to send a test email.", "error")
                return redirect(url_for("main.settings", tab="email"))

            try:
                message = build_settings_test_message()
                send_email_message(message)

                settings.email_test_status = "success"
                settings.email_tested_at = datetime.utcnow()
                settings.email_test_recipient = settings.test_email_recipient
                settings.email_test_message = "SMTP connection and test email succeeded."
                db.session.commit()

                flash("Test email sent successfully.", "success")
            except Exception as e:
                settings.email_test_status = "failed"
                settings.email_tested_at = datetime.utcnow()
                settings.email_test_recipient = settings.test_email_recipient
                settings.email_test_message = str(e)
                db.session.commit()

                flash(f"Test email failed: {e}", "error")

            return redirect(url_for("main.settings", tab="email"))

    if safeguard_form.submit_safeguard.data and safeguard_form.validate_on_submit():
        settings.live_send_password = safeguard_form.live_send_password.data.strip()

        db.session.commit()
        flash("Safeguard settings saved successfully.", "success")
        return redirect(url_for("main.settings", tab="safeguard"))

    if (template_form.submit_template.data or template_form.reset_template.data) and template_form.validate_on_submit():
        if template_form.submit_template.data:
            settings.default_email_subject = template_form.default_email_subject.data.strip()
            settings.default_email_body = template_form.default_email_body.data.strip()

            db.session.commit()
            flash("Template settings saved successfully.", "success")
            return redirect(url_for("main.settings", tab="template"))

        if template_form.reset_template.data:
            settings.default_email_subject = DEFAULT_EMAIL_SUBJECT
            settings.default_email_body = DEFAULT_EMAIL_BODY

            db.session.commit()
            flash("Template was reset to the default values.", "success")
            return redirect(url_for("main.settings", tab="template"))

    return render_template(
        "settings.html",
        email_form=email_form,
        safeguard_form=safeguard_form,
        template_form=template_form,
        active_tab=active_tab,
        settings_status=settings,
    )

@main.route("/history/<int:run_id>/export")
def export_run_csv(run_id):
    run = Run.query.get_or_404(run_id)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "run_id",
        "created_at",
        "run_status",
        "run_send_mode",
        "notification_id",
        "notification_type",
        "recipient_type",
        "recipient_name",
        "recipient_identifier",
        "to_email",
        "cc_emails",
        "student_id",
        "student_name",
        "activity_names",
        "failing_courses",
        "related_students",
        "subject",
        "sent_at",
        "notification_send_status",
        "notification_send_mode",
        "error_message",
    ])

    for notification in run.notifications:
        activity_names = json.loads(notification.activity_names_json or "[]")
        failing_courses = json.loads(notification.failing_courses_json or "[]")
        related_students = json.loads(notification.related_students_json or "[]")
        cc_emails = json.loads(notification.cc_emails or "[]")

        activity_names_text = "; ".join(activity_names)
        failing_courses_text = "; ".join(
            [f"{course['course_name']}: {course['current_grade']}" for course in failing_courses]
        )
        related_students_text = json.dumps(related_students)

        writer.writerow([
            run.id,
            run.created_at,
            run.status,
            run.send_mode,
            notification.id,
            notification.notification_type,
            notification.recipient_type,
            notification.recipient_name,
            notification.recipient_identifier,
            notification.to_email,
            "; ".join(cc_emails),
            notification.student_id or "",
            notification.student_name or "",
            activity_names_text,
            failing_courses_text,
            related_students_text,
            notification.subject,
            notification.sent_at,
            notification.send_status,
            notification.send_mode,
            notification.error_message or "",
        ])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=run_{run.id}_audit_export.csv"
        },
    )

@main.route("/history/<int:run_id>/export-exceptions")
def export_run_exceptions_csv(run_id):
    run = Run.query.get_or_404(run_id)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "run_id",
        "created_at",
        "run_status",
        "run_send_mode",
        "exception_id",
        "issue_type",
        "record_type",
        "record_key",
        "details",
    ])

    for exception in run.exceptions:
        writer.writerow([
            run.id,
            run.created_at,
            run.status,
            run.send_mode,
            exception.id,
            exception.issue_type,
            exception.record_type,
            exception.record_key or "",
            exception.details,
        ])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=run_{run.id}_exceptions_export.csv"
        },
    )