
import requests

GITHUB_API_URL = "https://api.github.com"

def get_all_pages(url):
    """catch all pages of a list-returning API, combine into one list."""
    items = []
    next_url = url
    params = {"per_page": 100}  

    while next_url:
        r = requests.get(next_url, params=params, timeout=10)

        # empty repo's commits API returns 409
        if r.status_code == 409:
            return items
        if r.status_code == 404:
            raise ValueError("Resource not found (404)")

        r.raise_for_status()

        data = r.json()
        if not isinstance(data, list):
            raise RuntimeError("Returned data is not a list, cannot paginate and concatenate")

        items.extend(data)

        # requests parses Link header into r.links
        next_url = r.links.get("next", {}).get("url")

        params = None

    return items


def get_user_repos(user, include_forks=False):
    if not user:
        raise ValueError("Username cannot be empty")
    url = f"{GITHUB_API_URL}/users/{user}/repos"
    repos = get_all_pages(url)
    return repos if include_forks else [r for r in repos if not r.get("fork")]


def get_repo_commit_count(user, repo):
    if not user or not repo:
        raise ValueError("Please include both user and repo")
    url = f"{GITHUB_API_URL}/repos/{user}/{repo}/commits"
    commits = get_all_pages(url)
    return len(commits)


def get_repo_commit_counts(user, include_forks=False):
    """return [(repo_name, commit_count)], output sorted by repo name for stable output."""
    repos = get_user_repos(user, include_forks=include_forks)
    pairs = []
    for r in repos:
        name = r.get("name")
        if not name:
            continue
        pairs.append((name, get_repo_commit_count(user, name)))
    # Sort by repo name, case insensitive
    pairs.sort(key=lambda t: t[0].lower())
    return pairs


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python HW3a_github_api.py <github_user>")
        raise SystemExit(1)

    user = sys.argv[1]
    try:
        # include forks in both steps to identify them
        repos_all = get_user_repos(user, include_forks=True)

        forked_names = set()
        for repo in repos_all:
            name = repo.get("name")
            if name and repo.get("fork"):
                forked_names.add(name)

        pairs = get_repo_commit_counts(user, include_forks=True)

        # print results
        for name, count in pairs:
            tag = " (fork)" if name in forked_names else ""
            print(f"Repo: {name}{tag} Number of commits: {count}")

    except Exception as e:
        print("Error:", e)
        raise SystemExit(2)
