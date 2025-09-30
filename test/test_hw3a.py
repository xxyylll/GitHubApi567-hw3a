
import time
import re
import pathlib
import pytest  
import sys
import os
sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))
import HW3a_github_api as hw3


SMOKE_USER = os.getenv("SMOKE_USER", "xxyylll")


def test_get_user_repos_smoke():
    """use smoke test user, check the return type and some fields."""
    repos = hw3.get_user_repos(SMOKE_USER)
    assert isinstance(repos, list)

    for r in repos[:5]:  # check first 5 repos
        assert isinstance(r, dict)
        assert "name" in r


def test_get_repo_commit_count_first_two_non_negative():
    """submitted user should have some repos, check first two repos have non-negative commit counts."""
    repos = hw3.get_user_repos(SMOKE_USER)
    names = [r.get("name") for r in repos if r.get("name")]
    for name in names[:2]:
        cnt = hw3.get_repo_commit_count(SMOKE_USER, name)
        assert isinstance(cnt, int)
        assert cnt >= 0
        time.sleep(0.3)


def test_get_repo_commit_counts_returns_sorted_pairs():
    """returns sorted (name, count) pairs."""
    pairs = hw3.get_repo_commit_counts(SMOKE_USER)
    assert isinstance(pairs, list)
    for item in pairs[:5]:
        assert isinstance(item, tuple) and len(item) == 2
        assert isinstance(item[0], str) and isinstance(item[1], int) and item[1] >= 0

    # check sorted by name, case insensitive
    names = [p[0] for p in pairs]
    assert names == sorted(names, key=lambda s: s.lower())


def test_user_not_found_raises():
    """return value error if user not found."""
    bad_user = "this_user_should_not_exist____xyz"
    with pytest.raises(ValueError):
        hw3.get_user_repos(bad_user)


def test_output_line_format_example_like():
    """check output line format"""
    pairs = hw3.get_repo_commit_counts(SMOKE_USER)
    if not pairs:
        return  # no public repos, skip
    name, count = pairs[0]
    line = f"Repo: {name} Number of commits: {count}"
    assert re.match(r'^Repo: .+ Number of commits: \d+$', line)