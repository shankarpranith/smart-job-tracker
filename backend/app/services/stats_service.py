from collections import Counter, defaultdict

from app.models.application import Application, ApplicationStats, StatusBreakdown, MonthlyCount

# Statuses that count as "the company responded" (i.e., not just Applied/Saved).
RESPONDED_STATUSES = {
    "Online Assessment", "Interview", "Offer", "Rejected", "Accepted",
}
# Statuses that count as having reached at least an interview stage.
INTERVIEWED_STATUSES = {"Interview", "Offer", "Accepted"}
# Statuses that count as a successful offer outcome.
OFFERED_STATUSES = {"Offer", "Accepted"}


def compute_stats(applications: list[Application]) -> ApplicationStats:
    total = len(applications)

    status_counter = Counter(app.status.value for app in applications)
    status_breakdown = [
        StatusBreakdown(status=status, count=count)
        for status, count in status_counter.items()
    ]

    interviews = sum(1 for app in applications if app.status.value in INTERVIEWED_STATUSES)
    offers = sum(1 for app in applications if app.status.value in OFFERED_STATUSES)
    rejections = status_counter.get("Rejected", 0)
    responded = sum(1 for app in applications if app.status.value in RESPONDED_STATUSES)

    response_rate = round((responded / total) * 100, 1) if total else 0.0
    interview_rate = round((interviews / total) * 100, 1) if total else 0.0
    offer_rate = round((offers / total) * 100, 1) if total else 0.0

    # Group by month using created_at (when the application was added to our system).
    monthly_counts = defaultdict(int)
    for app in applications:
        month_key = app.created_at.strftime("%Y-%m")
        monthly_counts[month_key] += 1

    applications_over_time = [
        MonthlyCount(month=month, count=count)
        for month, count in sorted(monthly_counts.items())
    ]

    return ApplicationStats(
        total_applications=total,
        status_breakdown=status_breakdown,
        interviews=interviews,
        offers=offers,
        rejections=rejections,
        response_rate=response_rate,
        interview_rate=interview_rate,
        offer_rate=offer_rate,
        applications_over_time=applications_over_time,
    )