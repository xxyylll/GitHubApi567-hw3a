[![CircleCI](https://circleci.com/gh/xxyylll/GitHubApi567-hw3a/tree/HW03a_Mocking.svg?style=svg)](https://circleci.com/gh/xxyylll/GitHubApi567-hw3a/tree/HW03a_Mocking)

This branch replaces live tests with fully mocked unit tests using `unittest.mock`; no real GitHub API calls are made.


This folder contains a simplified GitHub API helper script `HW3a_github_api.py`.


Usage:
1. Install requirements (project root has a `requirements.txt`):

```bash
python3 -m pip install -r requirements.txt
```

2. Run the script:

```bash
python3 HW3a_github_api.py <github_user>
```

Output format:

- Each matching repository prints one line exactly in this format:

```
Repo: <repo_name> Number of commits: <count>
```

How to test:

- From the `HW3` directory run pytest:

```bash
pytest -q
```

Notes (behavior):

- Pagination via `Response.links` (the script follows `rel="next"` links).
- Empty repositories: GitHub may return 409 on commits endpoints; the script treats this as zero commits.
- Forked repos are included and labeled (fork). Output is stably sorted by repository name (case-insensitive).
- If you hit API rate limits, GitHub returns 403 with rate-limit info in headers; consider using an authenticated request (token) or retrying later.
