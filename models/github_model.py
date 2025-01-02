from typing import Optional, List

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship


class PRTaskReview(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    analysis_result: Optional[str] = None
    status: Optional[str] = Field(default="pending")
    task_id: Optional[str] = None

    # Relationship to PullRequest
    pull_requests: List["PullRequest"] = Relationship(back_populates="pr_task_review")


class PullRequestPydantic(BaseModel):
    repo_url: str
    pr_number: int
    github_token: str


class PullRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    repo_url: str
    pr_number: int
    github_token: str
    pr_changes: Optional[str] = None
    pr_task_review_id: Optional[int] = Field(
        default=None, foreign_key="prtaskreview.id"
    )
    analysis_result: Optional[str] = None
    pr_task_review: Optional[PRTaskReview] = Relationship(
        back_populates="pull_requests"
    )
