import random

# Global configuration to match README deterministic reproducibility requirements
RANDOM_SEED = 42
CATEGORIES = ["Personal Loan", "Home Loan", "Auto Loan", "Education Loan", "Business Loan"]
STATUSES = ["Submitted", "Under Review", "Approved", "Rejected", "Disbursed"]

def generate_dataset(seed=RANDOM_SEED):
    random.seed(seed)
    records = []
    
    # Ensuring base criteria are met perfectly by seeding at least one of each initially
    for idx, cat in enumerate(CATEGORIES):
        records.append({
            "record_id": f"LNK-{1000 + idx}",
            "category": cat,
            "status": STATUSES[idx % len(STATUSES)],
            "loan_amount_inr": random.randint(100000, 5000000),
            "days_since_created": random.randint(0, 30),
            "flagged_for_fraud_review": random.choice([True, False, False, False])
        })
        
    # Fill up to 45 records deterministically
    for i in range(len(CATEGORIES), 45):
        records.append({
            "record_id": f"LNK-{1000 + i}",
            "category": random.choice(CATEGORIES),
            "status": random.choice(STATUSES),
            "loan_amount_inr": random.randint(100000, 5000000),
            "days_since_created": random.randint(0, 30),
            "flagged_for_fraud_review": random.uniform(0, 1) < 0.22 # Targets the ~20% middle range
        })
    return records

LOAN_APPLICATIONS = generate_dataset()

def check_loan_application_status(record_id: str) -> dict:
    """Task 6: Returns status details alongside an algorithmic escalation score."""
    record = next((r for r in LOAN_APPLICATIONS if r["record_id"] == record_id), None)
    if not record:
        return {"error": "Application record not found."}
    
    # Formula: normalized recency factor * 0.4 + fraud flag * 0.6
    # Days since created are bounded. Older requests require a higher operational score.
    normalized_recency = record["days_since_created"] / 30.0
    fraud_weight = 0.6 if record["flagged_for_fraud_review"] else 0.0
    recency_weight = normalized_recency * 0.4
    escalation_score = round(fraud_weight + recency_weight, 2)
    
    return {
        "record_id": record["record_id"],
        "status": record["status"],
        "loan_amount_inr": record["loan_amount_inr"],
        "days_since_created": record["days_since_created"],
        "flagged_for_fraud_review": record["flagged_for_fraud_review"],
        "escalation_score": escalation_score
    }

if __name__ == "__main__":
    # Validate structure criteria on run
    from collections import Counter
    cats = [r["category"] for r in LOAN_APPLICATIONS]
    stats = [r["status"] for r in LOAN_APPLICATIONS]
    fraud_pct = (sum(1 for r in LOAN_APPLICATIONS if r["flagged_for_fraud_review"]) / len(LOAN_APPLICATIONS)) * 100
    print(f"Total Generated: {len(LOAN_APPLICATIONS)}")
    print(f"Categories Count: {dict(Counter(cats))}")
    print(f"Statuses Count: {dict(Counter(stats))}")
    print(f"Fraud Percentage: {fraud_pct:.2f}%")
