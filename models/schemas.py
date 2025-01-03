from typing import Optional

from pydantic import BaseModel


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    # results: Results
    message: Optional[str] = None

    class Config:
        orm_mode = True


class PullRequestPydantic(BaseModel):
    repo_url: str
    pr_number: int
    github_token: str
