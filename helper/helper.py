import logging

import requests

from helper.statics import GithubStatics
from models.database_engine import SessionLocal
from models.github_model import PullRequest

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def fetch_pr_files(pr_url, headers):
    """
    Fetches the list of files in a pull request.

    Args:
        pr_url (str): API URL of the pull request.
        headers (dict): Headers containing authorization details.

    Returns:
        list: List of files in the pull request with their details.

    Raises:
        RuntimeError: If the API call fails or the response is invalid.
    """
    try:
        logger.info(f"Fetching files from PR URL: {pr_url}/files")
        response = requests.get(f"{pr_url}/files", headers=headers)
        response.raise_for_status()
        pr_files = response.json()
        logger.info(f"Successfully fetched {len(pr_files)} file(s) from the PR.")
        return pr_files
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch files for PR: {e}")
        raise RuntimeError(f"Error fetching PR files: {e}")


def process_pr_files(pr_files):
    """
    Processes the files in a pull request and formats the changes.

    Args:
        pr_files (list): List of files in the pull request.

    Returns:
        str: Formatted string containing details of the file changes.
    """
    logger.info("Processing PR files to generate changes.")
    git_changes = []
    for file in pr_files:
        filename = file.get("filename", "Unknown file")
        status = file.get("status", "Unknown status")
        patch = file.get("patch", "No patch available")
        logger.debug(f"Processing file: {filename}, Status: {status}")
        git_changes.append(
            f"File: {filename}\nStatus: {status}\nPatch:\n{patch}\n{'-' * 80}"
        )
    logger.info("Successfully processed all files.")
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
        # Validate inputs
        logger.info("Validating input data for the pull request.")
        if not pr_data.github_token:
            logger.error("GitHub token is missing.")
            raise ValueError("GitHub token is required for authentication.")
        if not pr_data.repo_url or not pr_data.pr_number:
            logger.error("Repository URL or PR number is missing.")
            raise ValueError("Both repository URL and PR number are required.")

        # Extract owner and repo from the URL
        url_data = pr_data.repo_url.strip("/").split("/")
        if len(url_data) < 2:
            logger.error("Invalid repository URL format.")
            raise ValueError("Invalid repository URL format.")
        owner, repo = url_data[3], url_data[4]
        logger.info(f"Repository extracted: Owner={owner}, Repo={repo}")

        # Construct the API URL
        pr_url = (
            f"{GithubStatics.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_data.pr_number}"
        )
        logger.info(f"Constructed Pull Request API URL: {pr_url}")

        # Fetch pull request details
        logger.info("Fetching pull request details from GitHub API.")
        headers = {"Authorization": f"Bearer {pr_data.github_token}"}
        pr_response = requests.get(pr_url, headers=headers)
        pr_response.raise_for_status()
        pr_data_response = pr_response.json()
        logger.info("Successfully fetched pull request details.")

        # Fetch PR file changes and process them
        pr_files = fetch_pr_files(pr_data_response.get("url"), headers)
        git_changes = process_pr_files(pr_files)
        return git_changes

    except ValueError as e:
        logger.error(f"Validation error: {e.__str__()}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e.__str__()}")
        raise RuntimeError(f"Failed to fetch pull request details: {e.__str__()}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e.__str__()}")
        raise


def save_analysis(pr_data, analysis_result):
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
        return pr
