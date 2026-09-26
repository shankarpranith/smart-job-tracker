import json
from datetime import date, timedelta

import boto3

from app.config import AWS_REGION, SNS_TOPIC_ARN
from app.repositories import application_repository as repo

_sns_client = boto3.client("sns", region_name=AWS_REGION)


def build_reminder_message(applications_today, applications_tomorrow) -> str:
    """Build a plain-text summary of upcoming follow-ups."""
    lines = ["Job Application Follow-Up Reminders", ""]

    if applications_today:
        lines.append(f"Follow up TODAY ({len(applications_today)}):")
        for app in applications_today:
            lines.append(f"  - {app.job_title} at {app.company}")
        lines.append("")

    if applications_tomorrow:
        lines.append(f"Follow up TOMORROW ({len(applications_tomorrow)}):")
        for app in applications_tomorrow:
            lines.append(f"  - {app.job_title} at {app.company}")

    return "\n".join(lines)


def handler(event, context):
    """
    Entry point for the scheduled EventBridge rule.
    Runs once daily. Checks for applications with a follow_up_date
    of today or tomorrow, across ALL users, and sends one summary
    email via SNS if any are found.
    """
    today = date.today()
    tomorrow = today + timedelta(days=1)

    applications_today = repo.find_by_follow_up_date(today.isoformat())
    applications_tomorrow = repo.find_by_follow_up_date(tomorrow.isoformat())

    total_found = len(applications_today) + len(applications_tomorrow)

    if total_found == 0:
        print("No upcoming follow-ups found. No notification sent.")
        return {"statusCode": 200, "body": json.dumps({"remindersSent": 0})}

    message = build_reminder_message(applications_today, applications_tomorrow)

    _sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=f"Job Tracker: {total_found} follow-up reminder(s)",
        Message=message,
    )

    print(f"Sent reminder for {total_found} application(s).")
    return {"statusCode": 200, "body": json.dumps({"remindersSent": total_found})}