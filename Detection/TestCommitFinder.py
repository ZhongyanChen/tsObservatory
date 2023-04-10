# This script documents all commits in development branch changing test files by file names
from git import Repo
import csv
from pathlib import Path
import os
from Util import Util


# This function checks if a given commit contains changes made in test files
def has_test_files_change(input_commit):
    for file in iter(input_commit.stats.files):

        file_name = Path(file).name

        # might need to refactor to use any() if more keywords are being searched
        if (".java" in file_name) and ("Test" in file_name):
            return True  # Once the first test file in this commit is found, the check is done.


# This function finds all commits in the development branch
# by searching the first parent of every commit in this branch
def get_development_branch_commits(start_commit):
    current_commit = start_commit  # Defining current_commit for better readability in the while loop
    commits_in_dev_branch = []

    while True:

        if len(current_commit.parents) != 0:
            commits_in_dev_branch.append(current_commit)
            current_commit = current_commit.parents[0]

        else:  # The statement below will only be reached if this is the initial commit
            commits_in_dev_branch.append(current_commit)
            break

    return commits_in_dev_branch


# This function creates a csv containing details of target commits(sha, parents, changed files, summary)
def get_target_commits(output_file, dev_branch_commits):
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:

        spamwriter = csv.writer(csvfile)

        for commit in dev_branch_commits:
            if has_test_files_change(commit):
                # print(commit.stats.files)
                spamwriter.writerow([commit.hexsha, commit.stats.files, commit.parents, commit.summary])


def get_target_sha(repository_path, index):
    target_repo_name = Util.get_repository_name_from_path(repository_path)
    target_csv_name = Util.get_target_commits_file_name(target_repo_name)
    output_directory = Util.get_target_commits_folder(target_repo_name)

    repo = Repo(repository_path)
    commits = list(repo.iter_commits())
    dev_branch_commits = get_development_branch_commits(commits[index])

    try:
        os.makedirs(output_directory)
    except FileExistsError:
        print("Directory exists")

    with open(os.path.join(output_directory, target_csv_name), 'w', newline='', encoding='utf-8') as csvfile:

        spamwriter = csv.writer(csvfile)

        for commit in dev_branch_commits:
            if has_test_files_change(commit):
                # print(commit.stats.files)
                spamwriter.writerow([commit.hexsha])
