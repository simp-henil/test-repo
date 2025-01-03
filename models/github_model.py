from typing import Optional

from sqlmodel import SQLModel, Field


class PullRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    repo_url: str
    pr_number: int
    github_token: str
    pr_changes: Optional[str] = None
    pr_task_review_id: Optional[str] = None
    analysis_result: Optional[str] = None
    status: Optional[str] = None

