FOUNDATION_SCHEMA = """
CREATE TABLE IF NOT EXISTS task_requests (
    request_id TEXT PRIMARY KEY,
    source_channel TEXT NOT NULL,
    sender TEXT NOT NULL,
    raw_message TEXT NOT NULL,
    task_intent TEXT NOT NULL,
    priority TEXT NOT NULL,
    attachments_json TEXT NOT NULL,
    authorization_context_json TEXT NOT NULL,
    idempotency_key TEXT
);

CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,
    role_group TEXT NOT NULL,
    actor TEXT NOT NULL,
    critic TEXT NOT NULL,
    status TEXT NOT NULL,
    input_json TEXT NOT NULL,
    workspace TEXT NOT NULL,
    artifact_paths_json TEXT NOT NULL,
    retry_count INTEGER NOT NULL,
    timeout_seconds INTEGER NOT NULL,
    failure_reason TEXT
);

CREATE TABLE IF NOT EXISTS critic_reviews (
    review_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    review_result TEXT NOT NULL,
    score INTEGER NOT NULL,
    issues_json TEXT NOT NULL,
    approved INTEGER NOT NULL,
    return_to_actor INTEGER NOT NULL,
    handoff_note TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notification_events (
    notification_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    target_channel TEXT NOT NULL,
    target_recipient TEXT NOT NULL,
    message_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    receipt_required INTEGER NOT NULL,
    retry_policy TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS score_records (
    score_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    scored_role TEXT NOT NULL,
    scorer_role TEXT NOT NULL,
    score INTEGER NOT NULL,
    rating TEXT NOT NULL,
    review_summary TEXT NOT NULL,
    created_at TEXT NOT NULL,
    month_bucket TEXT NOT NULL
);
"""
