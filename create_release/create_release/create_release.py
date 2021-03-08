from datetime import datetime
import os

import click
from git import Repo


def get_file_version(path: str) -> str:
    with open(os.path.join(path, 'VERSION')) as version_file:
        version = version_file.readline().strip().replace('_', '.')
        print(f'Version from file is: {version}')
        return version


def create_release(path: str):
    print('Create release ...')
    repo = Repo(path)

    latest_tag = repo.git.describe('--abbrev=0', '--tags')
    (last_version_release, last_version_package) = f'{latest_tag}'.split('-')
    print(f'Latest tag is: {latest_tag}')

    relevant_commits = get_relevant_commits(repo, latest_tag)

    file_version = get_file_version(path)
    if file_version == last_version_release:
        new_release = f'{last_version_release}-{int(last_version_package) + 1}'
    else:
        new_release = f'{file_version}-1'
    if len(relevant_commits) > 0:
        print(f'New release is: {new_release}')
        changelog = create_changelog_entry(new_release, relevant_commits)
        create_changelog(path, changelog)
        create_tag(repo, new_release)
        commit_and_push(repo, new_release)
        create_release_file(path, new_release, 'true')
    else:
        print('Skip release since there are no release relevant commits.')
        create_release_file(path, f'{last_version_release}-{last_version_package}', 'false')


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
    for commit in commits:
        commit_message = commit.message
        if commit_message.startswith('fix: ') or commit_message.startswith('feat: '):
            relevant_commits.append(commit_message)
    return relevant_commits


@click.command()
@click.option('--path',
              required=True,
              help='Path to the Git repository')
def main(path: str):
    create_release(path)


if __name__ == '__main__':
    main(None)
