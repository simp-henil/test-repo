import logging

from fastapi import APIRouter, HTTPException
from starlette.responses import JSONResponse

from helper.helper import get_all_pull_request, save_analysis
from models.database_engine import init_db, SessionLocal
from models.github_model import PullRequest, PullRequestPydantic

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database at startup
init_db()

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/analyze-pr", response_model=dict)
async def github_analyze(pr_data: PullRequestPydantic):
    try:
        logger.info(f"Received PR data: {pr_data}")

        # Validate pull request data
        if not pr_data.repo_url or not pr_data.pr_number:
            logger.error("Repository URL or PR number is missing.")
            raise HTTPException(status_code=400, detail="Invalid pull request data.")

        # Fetch and process pull request details
        analysis_result = get_all_pull_request(pr_data)
        logger.info(f"Analysis result: {analysis_result}")

        # Save analysis to the database
        saved_pr = save_analysis(pr_data, analysis_result)
        logger.info(f"Saved PR analysis: {saved_pr}")

        return JSONResponse(
            {"pr_id": saved_pr.id, "analysis": saved_pr.analysis_result}
        )
    except Exception as e:
        logger.error(f"Error in analyzing pull request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
