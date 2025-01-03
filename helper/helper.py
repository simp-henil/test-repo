import logging

import requests

from helper.statics import GithubStatics
from models.database_engine import SessionLocal
from models.github_model import PullRequest

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def fetch_pr_files(pr_url, headers):
    try:
        logger.info(f"Fetching files from PR URL: {pr_url}/files")
        response = requests.get(f"{pr_url}/files", headers=headers)
        response.raise_for_status()
        pr_files = response.json()
        logger.info(f"Fetched {len(pr_files)} file(s) from the PR.")
        return pr_files
    except requests.exceptions.RequestException as e:
        logger.exception("Failed to fetch files for the pull request.")
        raise RuntimeError(f"Error fetching PR files: {e}")


def process_pr_files(pr_files):
    logger.info("Processing pull request files for changes.")
    git_changes = []
    for file in pr_files:
        filename = file.get("filename", "Unknown file")
        status = file.get("status", "Unknown status")
        patch = file.get("patch", "No patch available")
        logger.debug(f"Processing file: {filename}, Status: {status}")
        git_changes.append(
            f"File: {filename}\nStatus: {status}\nPatch:\n{patch}\n{'-' * 80}"
        )
    logger.info("Successfully processed all PR files.")
    return "\n\n".join(git_changes)


def get_all_pull_request(pr_data):
    """
    Fetches and processes the details of a pull request.

    Args:
        pr_data (object): Object containing `repo_url`, `pr_number`, and `github_token`.

    Returns:
        str: Formatted string of all changes in the pull request.

    Raises:
        ValueError: If required fields in `pr_data` are missing or invalid.
        RuntimeError: If the API call fails or data is incomplete.
    """
    try:
        logger.info("Starting pull request analysis.")
        if not pr_data.github_token:
            logger.error("GitHub token is missing.")
            raise ValueError("GitHub token is required for authentication.")
        if not pr_data.repo_url or not pr_data.pr_number:
            logger.error("Repository URL or PR number is missing.")
            raise ValueError("Both repository URL and PR number are required.")

        url_data = pr_data.repo_url.strip("/").split("/")
        if len(url_data) < 5:
            logger.error(f"Invalid repository URL: {pr_data.repo_url}")
            raise ValueError("Invalid repository URL format.")
        owner, repo = url_data[3], url_data[4]
        logger.info(f"Extracted repository details: Owner={owner}, Repo={repo}")

        pr_url = (
            f"{GithubStatics.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_data.pr_number}"
        )
        logger.info(f"Constructed Pull Request API URL: {pr_url}")

        logger.info("Fetching pull request details from GitHub API.")
        headers = {"Authorization": f"Bearer {pr_data.github_token}"}
        pr_response = requests.get(pr_url, headers=headers)
        pr_response.raise_for_status()
        pr_data_response = pr_response.json()
        logger.info("Pull request details successfully fetched.")

        pr_files = fetch_pr_files(pr_data_response.get("url"), headers)
        git_changes = process_pr_files(pr_files)
        logger.info("Pull request analysis completed.")
        return git_changes

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch pull request details: {e}")
        raise RuntimeError(f"Failed to fetch pull request details: {e}")
    except Exception as e:
        logger.exception("An unexpected error occurred during pull request analysis.")
        raise


def save_analysis(pr_data, analysis_result):
    try:
        logger.info(f"Saving analysis result for PR #{pr_data.pr_number}.")
        with SessionLocal() as session:
            pr = PullRequest(
                repo_url=pr_data.repo_url,
                pr_number=pr_data.pr_number,
                github_token=pr_data.github_token,
                pr_changes=analysis_result,
            )
            session.add(pr)
            session.commit()
            session.refresh(pr)
            logger.info(f"Analysis saved successfully for PR #{pr_data.pr_number}.")
            return pr
    except Exception as e:
        logger.exception("Failed to save the pull request analysis.")
        raise
