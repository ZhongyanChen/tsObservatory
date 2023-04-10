import csv
from git import Repo
import os
from Util import Util


# Calculate the lines of code of test files for every target commit
def compute_test_growth(repository_path, target_commit_shas):
    repo = Repo(repository_path)
    total = 0
    total_loc = []

    for sha in target_commit_shas:

        commit = repo.commit(sha)
        natural_growth = 0

        print(sha)

        for key in commit.stats.files:
            if (".java" in key) and ("Test" in key):
                natural_growth += commit.stats.files[key]['insertions'] - commit.stats.files[key]['deletions']

        total += natural_growth
        total_loc.append([sha, total])

    return total_loc


# Write test growth data to a CSV file
def write_test_growth(data, output_file_path):

    # Write [sha, test loc] pairs into a CSV file
    with open(output_file_path, "w", newline='') as csvfile:

        spamwriter = csv.writer(csvfile)

        for i in range(0, len(data)):
            spamwriter.writerow(data[i])


def get_test_growth(repository_path):
    target_repo_name = Util.get_repository_name_from_path(repository_path)
    commits = Util.get_all_sha(target_repo_name)

    # For test growth generation
    growth_file_name = Util.get_test_growth_file_name(target_repo_name)
    graph_data_folder = Util.get_graph_data_folder(target_repo_name)

    try:
        os.makedirs(graph_data_folder)
    except FileExistsError:
        print("Directory exists")

    test_growth_data = compute_test_growth(repository_path, commits)
    write_test_growth(test_growth_data, os.path.join(graph_data_folder, growth_file_name))
