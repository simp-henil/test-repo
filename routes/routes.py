import json

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, Depends, Path
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from background_processor.pr_review_celery_job import analyze_git_pr
from helper.helper import (
    logger,
    get_all_pull_request,
)
from models.database_engine import SessionLocal
from models.github_model import PullRequest
from models.schemas import (
    PullRequestPydantic,
    TaskStatusResponse,
)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")


@router.post("/analyze-pr", response_model=dict)
async def analyze_pr(pr_data: PullRequestPydantic, db: Session = Depends(get_db)):
    try:
        pr_task = PullRequest(
            repo_url=pr_data.repo_url,
            pr_number=pr_data.pr_number,
            github_token=pr_data.github_token,
        )
        pr_task.pr_changes = get_all_pull_request(pr_data)
        db.add(pr_task)
        db.commit()
        db.refresh(pr_task)

        celery_task = analyze_git_pr.apply_async(args=[pr_task.pr_changes])

        pr_task.pr_task_review_id = celery_task.id
        db.commit()

        return {"task_id": pr_task.pr_task_review_id, "status": pr_task.status}
    except Exception as e:
        logger.error(f"Error while analyzing PR: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_status(task_id: str):
    try:
        celery_task = AsyncResult(task_id)

        task_status = celery_task.status
        task_result = celery_task.result

        response = {
            "task_id": task_id,
            "status": task_status,
        }

        if task_status == "SUCCESS":
            response["result"] = task_result
        elif task_status == "FAILURE":
            response["error"] = str(celery_task.info)

        elif task_status == "PENDING":
            response["result"] = None
            response["error"] = None

        return response

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error fetching task status: {str(e)}"
        )


@router.get("/results/{task_id}", response_model=dict)
async def get_task_status(
    task_id: str = Path(..., description="The ID of the task to retrieve status for")
):
    try:
        db = SessionLocal()
        task = db.query(PullRequest).filter_by(pr_task_review_id=task_id).first()

        return {
            "task_id": task.pr_task_review_id,
            "status": task.status,
            "results": json.loads(task.analysis_result),
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing task: {str(e)}")
