from smolagents import tool
import requests
import re

@tool
def get_repo_info(github_url: str) -> str:
    """Get repository information including size and description using GitHub API.

    Args:
        ctx: The context.
        github_url: The GitHub repository URL.

    Returns:
        str: Repository information as JSON.
    """
    match = re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', github_url)
    if not match:
        return "Invalid GitHub URL format"
    
    owner, repo = match.groups()
    # headers = {'Authorization': f'token {ctx.deps.github_token}'} if ctx.deps.github_token else {}
    headers = {}
    
    # response = await ctx.deps.client.get(
    response = requests.get(
        f'https://api.github.com/repos/{owner}/{repo}',
        headers=headers
    )
    
    if response.status_code != 200:
        return f"Failed to get repository info: {response.text}"
    
    data = response.json()
    size_mb = data['size'] / 1024
    
    return data
    # return (
    #     f"Repository: {data['full_name']}\n"
    #     f"Description: {data['description']}\n"
    #     f"Size: {size_mb:.1f}MB\n"
    #     f"Stars: {data['stargazers_count']}\n"
    #     f"Language: {data['language']}\n"
    #     f"Created: {data['created_at']}\n"
    #     f"Last Updated: {data['updated_at']}"
    # )


@tool
def get_repo_structure(github_url: str) -> str:
    """Get the directory structure of a GitHub repository.

    Args:
        ctx: The context.
        github_url: The GitHub repository URL.

    Returns:
        str: Directory structure.
    """
    match = re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', github_url)
    if not match:
        return "Invalid GitHub URL format"
    
    owner, repo = match.groups()
    # headers = {'Authorization': f'token {ctx.deps.github_token}'} if ctx.deps.github_token else {}
    headers = {}
    
    response = requests.get(
        f'https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1',
        headers=headers
    )
    
    if response.status_code != 200:
        # Try with master branch if main fails
        response = requests.get(
            f'https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1',
            headers=headers
        )
        if response.status_code != 200:
            return f"Failed to get repository structure: {response.text}"
    
    data = response.json()
    tree = data['tree']
    return tree
    
    # # Build directory structure
    # structure = []
    # for item in tree:
    #     if not any(excluded in item['path'] for excluded in ['.git/', 'node_modules/', '__pycache__/']):
    #         structure.append(f"{'📁 ' if item['type'] == 'tree' else '📄 '}{item['path']}")
    
    # return "\n".join(structure)

# @github_agent.tool
@tool
def get_file_content(github_url: str, file_path: str) -> str:
    """Get the content of a specific file from the GitHub repository.

    Args:
        ctx: The context.
        github_url: The GitHub repository URL.
        file_path: Path to the file within the repository.

    Returns:
        str: File content as a string.
    """
    match = re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', github_url)
    if not match:
        return "Invalid GitHub URL format"
    
    owner, repo = match.groups()
    # headers = {'Authorization': f'token {ctx.deps.github_token}'} if ctx.deps.github_token else {}
    headers = {}
    
    response = requests.get(
        f'https://raw.githubusercontent.com/{owner}/{repo}/main/{file_path}',
        headers=headers
    )
    
    if response.status_code != 200:
        # Try with master branch if main fails
        response = requests.get(
            f'https://raw.githubusercontent.com/{owner}/{repo}/master/{file_path}',
            headers=headers
        )
        if response.status_code != 200:
            return f"Failed to get file content: {response.text}"
    
    return response.text
    # return response.json()