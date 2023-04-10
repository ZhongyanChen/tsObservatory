# This script contains some general functions
# often used by other scripts.

import os
import pandas as pd
import MapSmellInstance
import Config
import csv


COMMIT_FILE_NAME = "_commits_about_tests.csv"
TEST_GROWTH_FILE_NAME = "_test_growth.csv"


# This function returns all types of test smells to be studied
def get_test_smells():
    test_smells = {"Assertion Roulette": "Assertion Roulette",
                   "Conditional Test Logic": "Conditional Test Logic",
                   "Constructor Initialization": "Constructor Initialization",
                   "Default Test": "Default Test",
                   "Duplicate Assert": "Duplicate Assert",
                   "Eager Test": "Eager Test",
                   "EmptyTest": "EmptyTest",
                   "Exception Catching Throwing": "Exception Catching Throwing",
                   "General Fixture": "General Fixture",
                   "IgnoredTest": "IgnoredTest",
                   "Lazy Test": "Lazy Test",
                   "Magic Number Test": "Magic Number Test",
                   "Mystery Guest": "Mystery Guest",
                   "Print Statement": "Print Statement",
                   "Redundant Assertion": "Redundant Assertion",
                   "Resource Optimism": "Resource Optimism",
                   "Sensitive Equality": "Sensitive Equality",
                   "Sleepy Test": "Sleepy Test",
                   "Unknown Test": "Unknown Test"}

    return test_smells


def get_repository_name_from_path(repository_path):
    return os.path.basename(repository_path)


def get_sha_from_file_path(filepath):
    filename = os.path.basename(filepath)
    component = filename.split()[-1].split(".")

    return component[0]


def get_committed_time_from_file_path(filepath):
    filename = os.path.basename(filepath)
    component = filename.split()

    return int(component[1])


def get_target_commits_folder(repository_name):
    return os.path.join(Config.get_target_commit_path(), repository_name)


def get_target_commits_file_name(repository_name):
    return repository_name + COMMIT_FILE_NAME


def get_smell_detection_results_folder(repository_name):
    return os.path.join(Config.get_smell_detection_path(), repository_name)


def get_test_growth_file_name(repository_name):
    return repository_name + TEST_GROWTH_FILE_NAME


def get_graph_data_folder(repository_name):
    return os.path.join(Config.get_graph_data_path(), repository_name)


def get_diff_folder(repository_name):
    return os.path.join(Config.get_line_diff_path(), repository_name)


def get_diff_file_name(csv_path_old, csv_path_new):
    return get_sha_from_file_path(csv_path_old) + ".." + get_sha_from_file_path(csv_path_new) + ".json"


def read_csv_by_smell(csv_path, smell_type, sort=True):
    dataframe = pd.read_csv(csv_path, names=['test path', 'production code path', 'detected smell', 'method name',
                                             'line numbers'], dtype={'line numbers': str}, keep_default_na=False)

    dataframe = dataframe[dataframe['detected smell'] == smell_type]
    data_list = dataframe.drop_duplicates().values.tolist()

    if sort:
        for row in data_list:
            # row[0] = Path(row[0])
            # row[1] = Path(row[1])
            row[4] = sorted(MapSmellInstance.get_line_numbers(row[4]))
        return data_list
    else:
        return data_list


def get_all_sha(repository_name, dictionary=False):
    commit_file_name = repository_name + COMMIT_FILE_NAME
    commit_file_folder = os.path.join(Config.get_target_commit_path(), repository_name)
    commit_file_path = os.path.join(commit_file_folder, commit_file_name)

    shas = []

    with open(commit_file_path, "r", newline='') as csvfile:
        spamreader = csv.reader(csvfile)

        for commit_sha in spamreader:
            shas.append(commit_sha[0])

    shas.reverse()

    if dictionary:
        return {"commits": shas}
    else:
        return shas


def get_all_smell_detection_result_paths(sha_list, smell_detection_result_folder):
    csv_paths = []
    smell_detection_results = os.listdir(smell_detection_result_folder)

    for sha in sha_list:
        result_file = [file for file in smell_detection_results if sha in file]
        result_path = os.path.join(smell_detection_result_folder, result_file[0])
        csv_paths.append(result_path)

    return csv_paths
