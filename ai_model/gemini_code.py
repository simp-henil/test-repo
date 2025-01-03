import json
import os

import google.generativeai as genai
from sqlmodel import Session

from models.github_model import PullRequest


def configure_genai():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    genai.configure(api_key=api_key)


def create_model():
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",
    }
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )
    return model


def analyze_code(model, code_snippet):
    chat_session = model.start_chat(history=[])

    instruction = f"""
    Analyze the following code for:
    1. Code style and formatting issues
    2. Potential bugs or errors
    3. Performance improvements
    4. Best practices
    Code snippet:
    {code_snippet}
    """

    response = chat_session.send_message(instruction)
    return json.loads(response.text)


def insert_analysis_to_db(session: Session, analysis_result: dict, task_id: str):
    existing_pr = (
        session.query(PullRequest).filter_by(pr_task_review_id=task_id).first()
    )

    if not existing_pr:
        raise ValueError(f"No pull request found with task ID: {task_id}")

    serialized_result = json.dumps(analysis_result)

    existing_pr.analysis_result = serialized_result

    session.commit()
    print(f"Analysis results successfully updated for task ID: {task_id}")
