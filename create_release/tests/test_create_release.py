from datetime import datetime
import builtins
from unittest import mock

from git import Commit
from create_release import create_release
from create_release.create_release import ReleaseType


def test_get_file_version(mocker):
    # Given
    mocker.patch.object(builtins, 'open', mocker.mock_open(read_data='1.2.3'))

    # When
    result = create_release.get_file_version('/some/path')

    # Then
    assert result == '1.2.3'


def test_create_changelog_entry():
    # Given
    fix_commit = 'fix: do this and that'
    feat_commit = 'feat: do this and that'
    commits = [
        fix_commit,
        feat_commit
    ]
    package = 'some software'
    version = '1.2.3-1'
    date = datetime.now().astimezone().strftime('%a, %d %b %Y ')
    expected_changelog = f'{package} ({version}) unstable; urgency=low\n\n' + \
        f'  * {fix_commit}' + \
        f'  * {feat_commit}\n' + \
        f' -- Kay Hannay <klinux@hannay.de>  {date}'

    # When
    result: str = create_release.create_changelog_entry(package, version, commits)

    # Then
    assert expected_changelog in result


def test_create_changelog(mocker):
    # Given
    existing_content = 'Latest entry in changelog'
    new_entry = f'efa2 (1.2.3-4) unstable; urgency=low\n\n' + \
        f'  * fix: some nice change\n' + \
        f' -- Kay Hannay <klinux@hannay.de>  Sun, 15 Nov 2020'
    file_mock = mocker.patch.object(builtins, 'open', mocker.mock_open(read_data=existing_content))

    # When
    create_release.create_changelog('/some/path', new_entry)

    # Then
    expected_calls = [
        mock.call('/some/path/debian/changelog', 'w'),
        mock.call('/some/path/debian/changelog', 'r')
    ]
    file_mock.assert_has_calls(expected_calls, any_order=True)
    handle = file_mock()
    handle.write.assert_called_once_with(f'{new_entry}\n\n'
                                         'Latest entry in changelog'),


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
    (commits, release_type) = create_release.get_relevant_commits(repo_mock, "1.2.3")

    # Then
    assert release_type is ReleaseType.FEATURE
    assert commit_mock1.message in commits
    assert commit_mock3.message in commits
    assert commit_mock2.message not in commits


def test_get_relevant_commits_type_breaking(mocker):
    # Given
    commit_mock1: Commit = mocker.Mock()
    commit_mock1.message = 'fix: do this and that\n\nfoo bar\n\nBREAKING CHANGE: foo'
    commit_mock2: Commit = mocker.Mock()
    commit_mock2.message = 'ci: do this and that'
    repo_mock = mocker.patch('git.Repo').return_value
    repo_mock.iter_commits.return_value = [
        commit_mock1,
        commit_mock2
    ]

    # When
    (result, release_type) = create_release.get_relevant_commits(repo_mock, "1.2.3")

    # Then
    assert release_type is ReleaseType.BREAKING
    assert commit_mock1.message in result
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
    (result, _) = create_release.get_relevant_commits(repo_mock, "1.2.3")

    # Then
    assert len(result) == 0


def test_create_tag(mocker):
    # Given
    version = '1.2.3-4'
    repo_mock = mocker.patch('git.Repo')

    # When
    create_release.create_tag(repo_mock, version)

    # Then
    repo_mock.create_tag.assert_called_once_with(version)


def test_commit_and_push(mocker):
    # Given
    version = '1.2.3-4'
    repo_mock = mocker.patch('git.Repo')

    # When
    create_release.commit_and_push(repo_mock, version)

    # Then
    expected_calls = [
        mock.call.git.config('user.email', 'klinux@hannay.de'),
        mock.call.git.config('user.name', 'create_release'),
        mock.call.git.add('.'),
        mock.call.git.commit(
        '-m', f'ci: create release {version}', author='create_release <klinux@hannay.de>'),
        mock.call.git.push('-u', 'origin', 'HEAD:main'),
        mock.call.git.push('-u', 'origin', '--tags')]
    assert repo_mock.mock_calls == expected_calls


def test_create_release_file(mocker):
    # Given
    file_mock = mocker.patch('builtins.open', mocker.mock_open())

    # When
    create_release.create_release_file('/some/path', '1.2.3-4', 'true')

    # Then
    file_mock.assert_called_once_with('/some/path/release_info.sh', 'w')
    handle = file_mock()
    handle.write.assert_called_once_with('VERSION=1.2.3-4\nCREATE_RELEASE=true')


def test_get_new_release_version_patch(mocker):
    # Given
    file_mock = mocker.patch('os.path.isfile')
    file_mock.return_value = False

    # When
    result: str = create_release.get_new_release_version(
        '2', '1.2.3', '.', create_release.ReleaseType.PATCH)

    # Then
    assert result == '1.2.4-1'


def test_get_new_release_version_feature(mocker):
    # Given
    file_mock = mocker.patch('os.path.isfile')
    file_mock.return_value = False

    # When
    result: str = create_release.get_new_release_version(
        '2', '1.2.3', '.', create_release.ReleaseType.FEATURE)

    # Then
    assert result == '1.3.0-1'


def test_get_new_release_version_breaking(mocker):
    # Given
    file_mock = mocker.patch('os.path.isfile')
    file_mock.return_value = False

    # When
    result: str = create_release.get_new_release_version(
        '2', '1.2.3', '.', create_release.ReleaseType.BREAKING)

    # Then
    assert result == '2.0.0-1'


def test_get_new_release_version_file_new_package(mocker):
    # Given
    file_mock = mocker.patch('os.path.isfile')
    file_mock.return_value = True
    mocker.patch.object(builtins, 'open', mocker.mock_open(read_data='1.2.3'))

    # When
    result: str = create_release.get_new_release_version(
        '2', '1.2.3', '/some/path', create_release.ReleaseType.NONE)

    # Then
    assert result == '1.2.3-3'


def test_get_new_release_version_file_new_release(mocker):
    # Given
    file_mock = mocker.patch('os.path.isfile')
    file_mock.return_value = True
    mocker.patch.object(builtins, 'open', mocker.mock_open(read_data='1.3.0'))

    # When
    result: str = create_release.get_new_release_version(
        '2', '1.2.3', '/some/path', create_release.ReleaseType.NONE)

    # Then
    assert result == '1.3.0-1'


def test_update_efalive_version(mocker):
    # Given
    file_mock = mocker.patch('builtins.open', mocker.mock_open())

    # When
    create_release.update_efalive_version('/some/path', '1.2.3-1')

    # Then
    file_mock.assert_called_once_with('/some/path/files/etc/efalive_version', 'w')
    handle = file_mock()
    handle.write.assert_called_once_with('1.2.3')
