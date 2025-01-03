import time

from celery import Celery, signals
from sqlmodel import Session

from ai_model.gemini_code import (
    insert_analysis_to_db,
    configure_genai,
    create_model,
    analyze_code,
)
from models.database_engine import SessionLocal, engine
from models.github_model import PullRequest

celery = Celery(
    __name__, broker="redis://0.0.0.0:6379/0", backend="redis://0.0.0.0:6379/0"
)


@signals.task_prerun.connect
def task_prerun_handler(task_id=None, **kwargs):
    """Update the status to 'pending' when a task starts."""
    print(f"Task Prerun Handler: Starting task {task_id}...")
    print(f"Arguments received in prerun: {kwargs}")
    db = SessionLocal()
    try:
        task = db.query(PullRequest).filter_by(pr_task_review_id=task_id).first()
        if task:
            task.status = "pending"
            db.commit()
            print(f"Task {task_id}: Status updated to 'pending'")
    finally:
        db.close()


@signals.task_postrun.connect
def task_postrun_handler(task_id=None, retval=None, **kwargs):
    """Update the status to 'success' when a task completes."""
    print(f"Task Postrun Handler: Task {task_id} completed...")
    print(f"Arguments received in postrun: {kwargs}")
    db = SessionLocal()
    try:
        task = db.query(PullRequest).filter_by(pr_task_review_id=task_id).first()
        if task:
            time.sleep(5)
            task.status = "success"
            db.commit()
            print(f"Task {task_id}: Status updated to 'success'. Result: {retval}")
    finally:
        db.close()


@signals.task_failure.connect
def task_failure_handler(task_id=None, **kwargs):
    """Update the status to 'failure' when a task fails."""
    print(f"Task Failure Handler: Task {task_id} failed...")
    print(f"Arguments received in failure: {kwargs}")
    db = SessionLocal()
    try:
        task = db.query(PullRequest).filter_by(pr_task_review_id=task_id).first()
        if task:
            task.status = "failure"
            db.commit()
            print(f"Task {task_id}: Status updated to 'failure'")
    finally:
        db.close()


@celery.task(bind=True)
def analyze_git_pr(self, pr_changes: str):
    """Celery task to analyze a pull request and store results in the database."""
    task_id = self.request.id

    configure_genai()
    model = create_model()

    try:
        ai_response = analyze_code(model, pr_changes)

        with Session(engine) as session:
            insert_analysis_to_db(session, ai_response, str(task_id))
        print("Analysis results successfully inserted into the database.")
    except Exception as db_error:
        print(f"Error inserting analysis results into the database: {db_error}")
        raise db_error
