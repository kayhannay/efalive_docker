from datetime import datetime
import builtins

from git import Commit
from create_release import create_release


def test_get_file_version(mocker):
    # Given
    mocker.patch.object(builtins, 'open', mocker.mock_open(read_data='1.2.3-4'))

    # When
    result = create_release.get_file_version('/some/path')

    # Then
    assert result == '1.2.3-4'


def test_create_changelog_entry():
    # Given
    fix_commit = 'fix: do this and that'
    feat_commit = 'feat: do this and that'
    commits = [
        fix_commit,
        feat_commit
    ]
    version = '1.2.3-1'
    date = datetime.now().astimezone().strftime('%a, %d %b %Y ')
    expected_changelog = f'efa2 ({version}) unstable; urgency=low\n\n' + \
        f'  * {fix_commit}' + \
        f'  * {feat_commit}\n' + \
        f' -- Kay Hannay <klinux@hannay.de>  {date}'

    # When
    result: str = create_release.create_changelog_entry(version, commits)

    # Then
    assert expected_changelog in result


def test_get_relevant_commits(mocker):
    # Given
    commit_mock1: Commit = mocker.Mock()
    commit_mock1.message = 'fix: do this and that'
    commit_mock2: Commit = mocker.Mock()
    commit_mock2.message = 'ci: do this and that'
    commit_mock3: Commit = mocker.Mock()
    commit_mock3.message = 'feat: do this and that'
    repo_mock = mocker.patch('git.Repo').return_value
    repo_mock.iter_commits.return_value = [
        commit_mock1,
        commit_mock2,
        commit_mock3
    ]

    # When
    result: [str] = create_release.get_relevant_commits(repo_mock)

    # Then
    assert commit_mock1.message in result
    assert commit_mock3.message in result
    assert commit_mock2.message not in result


def test_get_relevant_commits_empty(mocker):
    # Given
    commit_mock1: Commit = mocker.Mock()
    commit_mock1.message = 'ci: do this and that'
    repo_mock = mocker.patch('git.Repo').return_value
    repo_mock.iter_commits.return_value = [
        commit_mock1
    ]

    # When
    result: [str] = create_release.get_relevant_commits(repo_mock)

    # Then
    assert len(result) == 0
