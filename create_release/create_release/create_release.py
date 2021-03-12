from datetime import datetime
import os
from enum import Enum, unique

import click
from git import Repo


@unique
class ReleaseType(Enum):
    BREAKING = 3
    FEATURE = 2
    PATCH = 1
    NONE = 0


def has_version_file(path: str) -> bool:
    return os.path.isfile(os.path.join(path, 'VERSION'))


def get_file_version(path: str) -> str:
    with open(os.path.join(path, 'VERSION')) as version_file:
        version = version_file.readline().strip().replace('_', '.')
        print(f'Version from file is: {version}')
        return version


def create_release(path: str, dry_run: bool):
    print('Create release ...')
    repo = Repo(path)

    latest_tag = repo.git.describe('--abbrev=0', '--tags')
    (last_version_release, last_version_package) = f'{latest_tag}'.split('-')
    print(f'Latest tag is: {latest_tag}')

    (relevant_commits, release_type) = get_relevant_commits(repo, latest_tag)

    new_release = get_new_release_version(last_version_package, last_version_release, path,
                                          release_type)

    if release_type is not ReleaseType.NONE:
        print(f'New release is: {new_release}')
        changelog = create_changelog_entry(new_release, relevant_commits)
        create_changelog(path, changelog)
        if not dry_run:
            create_tag(repo, new_release)
            commit_and_push(repo, new_release)
        create_release_file(path, new_release, 'true')
    else:
        print('Skip release since there are no release relevant commits.')
        create_release_file(path, f'{last_version_release}-{last_version_package}', 'false')


def get_new_release_version(last_version_package, last_version_release, path, release_type):
    if has_version_file(path):
        file_version = get_file_version(path)
        if file_version == last_version_release:
            new_release = f'{last_version_release}-{int(last_version_package) + 1}'
        else:
            new_release = f'{file_version}-1'
    else:
        (breaking, feature, patch) = last_version_release.split('.')
        new_version_release = last_version_release
        if release_type is ReleaseType.BREAKING:
            new_version_release = f'{int(breaking) + 1}.0.0'
        elif release_type is ReleaseType.FEATURE:
            new_version_release = f'{breaking}.{int(feature) + 1}.0'
        elif release_type is ReleaseType.PATCH:
            new_version_release = f'{breaking}.{feature}.{int(patch) + 1}'
        new_release = f'{new_version_release}-1'
    return new_release


def create_release_file(path: str, version: str, release: str):
    with open(os.path.join(path, 'release_info.sh'), 'w') as release_file:
        release_file.write(f'VERSION={version}\nCREATE_RELEASE={release}')


def commit_and_push(repo: Repo, version: str):
    repo.git.add(".")
    repo.git.commit('-m',
                    f'ci: create release {version}',
                    author='create_release <klinux@hannay.de>')
    repo.git.push('-u', 'origin', 'HEAD:main')
    repo.git.push('-u', 'origin', '--tags')


def create_tag(repo: Repo, version: str):
    repo.create_tag(version)


def create_changelog_entry(version: str, commits: [str]):
    changelog = f'efa2 ({version}) unstable; urgency=low\n\n'
    for commit in commits:
        changelog = f'{changelog}  * {commit}'
    date = datetime.now().astimezone().strftime('%a, %d %b %Y %H:%M:%S %z')
    changelog = f'{changelog}\n -- Kay Hannay <klinux@hannay.de>  {date}'
    return changelog


def create_changelog(path: str, entry: str):
    changelog_file = os.path.join(path, 'debian', 'changelog')
    with open(changelog_file, 'r') as original:
        existing_changelog = original.read()
    new_changelog = f'{entry}\n\n{existing_changelog}'
    with open(changelog_file, 'w') as modified:
        modified.write(new_changelog)


def get_relevant_commits(repo: Repo, latest_tag: str) -> [str]:
    commits = repo.iter_commits(rev=f'{latest_tag}..HEAD')
    relevant_commits: [str] = []
    change_type = ReleaseType.NONE
    for commit in commits:
        commit_message = commit.message
        if commit_message.startswith('fix: ') or commit_message.startswith('perf: '):
            relevant_commits.append(commit_message)
            if change_type.value < ReleaseType.FEATURE.value:
                change_type = ReleaseType.PATCH
        elif commit_message.startswith('feat: '):
            relevant_commits.append(commit_message)
            if change_type.value < ReleaseType.BREAKING.value:
                change_type = ReleaseType.FEATURE
        if 'BREAKING CHANGE:' in commit_message:
            change_type = ReleaseType.BREAKING
    return relevant_commits, change_type


@click.command()
@click.option('--path',
              required=True,
              help='Path to the Git repository')
@click.option('--dry',
              required=False,
              is_flag=True,
              help='Dry run, do not commit')
def main(path: str, dry: bool = False):
    create_release(path, dry)


if __name__ == '__main__':
    main(None)
