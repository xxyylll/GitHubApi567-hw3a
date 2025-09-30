# test/test_hw3a_mock.py
import pytest
from unittest.mock import patch
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import HW3a_github_api as hw3

# fake response object
class FakeResp:
    def __init__(self, json_data=None, status_code=200, links=None):
        self._data = [] if json_data is None else json_data
        self.status_code = status_code
        self.links = links or {}

    def json(self):
        return self._data

    def raise_for_status(self):
        # simulate requests raising for 4xx/5xx
        if self.status_code >= 400:
            import requests
            raise requests.HTTPError(f"HTTP {self.status_code}")


def test_get_user_repos_pagination_and_filter():
    user = "mockuser"
    base = f"{hw3.GITHUB_API_URL}/users/{user}/repos"

    # define two pages of fake repos
    # page 1: 2 repos, one fork, has next
    page1 = FakeResp(
        json_data=[{"name": "Zoo", "fork": False}, {"name": "alpha", "fork": True}],
        status_code=200,
        links={"next": {"url": base + "?page=2"}},
    )
    # page 2: 1 repo, no fork, no next
    page2 = FakeResp(
        json_data=[{"name": "beta", "fork": False}],
        status_code=200,
        links={},
    )

    def fake_get(url, params=None, timeout=None):
        if url.startswith(base) and "page=2" in url:
            return page2
        if url.startswith(base):
            return page1
        pytest.fail(f"unexpected URL: {url}")

    with patch.object(hw3.requests, "get", side_effect=fake_get):
        repos_all = hw3.get_user_repos(user, include_forks=True)
        assert [r["name"] for r in repos_all] == ["Zoo", "alpha", "beta"]

        repos_no_forks = hw3.get_user_repos(user, include_forks=False)
        assert [r["name"] for r in repos_no_forks] == ["Zoo", "beta"]  # filtered out "alpha"


def test_get_repo_commit_count_pagination():
    user, repo = "mockuser", "Zoo"
    base = f"{hw3.GITHUB_API_URL}/repos/{user}/{repo}/commits"

    # next URL pagination
    c1 = FakeResp(json_data=[{"sha": "1"}], status_code=200, links={"next": {"url": base + "?page=2"}})
    # without next
    c2 = FakeResp(json_data=[{"sha": "2"}, {"sha": "3"}], status_code=200, links={})

    def fake_get(url, params=None, timeout=None):
        if url.startswith(base) and "page=2" in url:
            return c2
        if url.startswith(base):
            return c1
        pytest.fail(f"unexpected URL: {url}")

    with patch.object(hw3.requests, "get", side_effect=fake_get):
        assert hw3.get_repo_commit_count(user, repo) == 3


def test_empty_repo_commit_409_as_zero():
    user, repo = "mockuser", "emptyrepo"
    base = f"{hw3.GITHUB_API_URL}/repos/{user}/{repo}/commits"

    def fake_get(url, params=None, timeout=None):
        if url.startswith(base):
            return FakeResp(json_data=None, status_code=409, links={})
        pytest.fail(f"unexpected URL: {url}")

    with patch.object(hw3.requests, "get", side_effect=fake_get):
        assert hw3.get_repo_commit_count(user, repo) == 0


def test_user_not_found_raises_valueerror():
    user = "no_such_user_404"
    base = f"{hw3.GITHUB_API_URL}/users/{user}/repos"

    def fake_get(url, params=None, timeout=None):
        if url.startswith(base):
            return FakeResp(json_data={"message": "Not Found"}, status_code=404, links={})
        pytest.fail(f"unexpected URL: {url}")

    with patch.object(hw3.requests, "get", side_effect=fake_get):
        with pytest.raises(ValueError):
            hw3.get_user_repos(user, include_forks=True)


def test_get_repo_commit_counts_sorted_case_insensitive():
    user = "mockuser"
    repos_url = f"{hw3.GITHUB_API_URL}/users/{user}/repos"
    # provide 3 repos, mixed case names, some forks
    repos_page = FakeResp(
        json_data=[{"name": "beta", "fork": False}, {"name": "Alpha", "fork": True}, {"name": "Zoo", "fork": False}],
        status_code=200,
        links={},
    )
    # commits numbers: beta=1, Alpha=2, Zoo=0
    c_beta = f"{hw3.GITHUB_API_URL}/repos/{user}/beta/commits"
    c_alpha = f"{hw3.GITHUB_API_URL}/repos/{user}/Alpha/commits"
    c_zoo = f"{hw3.GITHUB_API_URL}/repos/{user}/Zoo/commits"

    def fake_get(url, params=None, timeout=None):
        if url.startswith(repos_url):
            return repos_page
        if url.startswith(c_beta):
            return FakeResp(json_data=[{"sha": "1"}], status_code=200)
        if url.startswith(c_alpha):
            return FakeResp(json_data=[{"sha": "1"}, {"sha": "2"}], status_code=200)
        if url.startswith(c_zoo):
            return FakeResp(json_data=[], status_code=200)
        pytest.fail(f"unexpected URL: {url}")

    with patch.object(hw3.requests, "get", side_effect=fake_get):
        pairs = hw3.get_repo_commit_counts(user, include_forks=True)
        # case insensitive 
        assert [name for name, _ in pairs] == ["Alpha", "beta", "Zoo"]
        # counts
        assert dict(pairs) == {"Alpha": 2, "beta": 1, "Zoo": 0}
