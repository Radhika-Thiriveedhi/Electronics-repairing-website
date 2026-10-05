from app.storage.json_store import read_json
from collections import defaultdict
from datetime import datetime

def get_platform_analytics():
    repairs = read_json("repairs.json")
    shops = read_json("shops.json")
    payments = read_json("payments.json")

    total_jobs = len(repairs)
    completed_jobs = sum(1 for r in repairs if r.get("status") == "Completed")
    active_repairs = sum(1 for r in repairs if r.get("status") in ["Received", "Diagnosing", "Waiting for Approval", "Repairing", "Ready for Collection"])
    
    total_sales = sum(float(p.get("amount", 0)) for p in payments if p.get("status") == "Completed")
    active_shops_count = len(shops)

    # Completion Rate
    completion_rate = round((completed_jobs / total_jobs * 100), 1) if total_jobs > 0 else 0.0

    # Category performance breakdown
    category_counts = defaultdict(int)
    for r in repairs:
        cat = r.get("category", "General")
        category_counts[cat] += 1

    # Monthly revenue data for Chart.js
    monthly_revenue = defaultdict(float)
    monthly_job_counts = defaultdict(int)
    for p in payments:
        if p.get("status") == "Completed":
            # Extract YYYY-MM
            created = p.get("created_at", "")
            month_key = created[:7] if len(created) >= 7 else "2026-10"
            monthly_revenue[month_key] += float(p.get("amount", 0))

    for r in repairs:
        created = r.get("created_at", "")
        month_key = created[:7] if len(created) >= 7 else "2026-10"
        monthly_job_counts[month_key] += 1

    # Sorted chart labels
    sorted_months = sorted(set(list(monthly_revenue.keys()) + list(monthly_job_counts.keys())))
    if not sorted_months:
        sorted_months = ["2026-08", "2026-09", "2026-10"]

    chart_labels = sorted_months
    chart_revenue = [monthly_revenue[m] for m in sorted_months]
    chart_jobs = [monthly_job_counts[m] for m in sorted_months]

    return {
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "active_repairs": active_repairs,
        "total_sales": total_sales,
        "active_shops_count": active_shops_count,
        "completion_rate": completion_rate,
        "category_counts": dict(category_counts),
        "chart_labels": chart_labels,
        "chart_revenue": chart_revenue,
        "chart_jobs": chart_jobs
    }

def get_shop_analytics(shop_id):
    repairs = [r for r in read_json("repairs.json") if r.get("shop_id") == shop_id]
    payments = [p for p in read_json("payments.json") if p.get("shop_id") == shop_id and p.get("status") == "Completed"]
    reviews = [rev for rev in read_json("reviews.json") if rev.get("shop_id") == shop_id]

    total_jobs = len(repairs)
    completed_jobs = sum(1 for r in repairs if r.get("status") == "Completed")
    pending_requests = sum(1 for r in repairs if r.get("status") == "Received")
    awaiting_approval = sum(1 for r in repairs if r.get("status") == "Waiting for Approval")
    in_progress = sum(1 for r in repairs if r.get("status") in ["Diagnosing", "Repairing"])
    ready_for_pickup = sum(1 for r in repairs if r.get("status") == "Ready for Collection")

    total_revenue = sum(float(p.get("amount", 0)) for p in payments)
    
    avg_rating = 0.0
    if reviews:
        avg_rating = round(sum(r.get("rating", 5) for r in reviews) / len(reviews), 1)

    return {
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "pending_requests": pending_requests,
        "awaiting_approval": awaiting_approval,
        "in_progress": in_progress,
        "ready_for_pickup": ready_for_pickup,
        "total_revenue": total_revenue,
        "avg_rating": avg_rating,
        "reviews_count": len(reviews)
    }
