import os
from git import Repo
from Util import Util

CHECKOUT_COMMAND = "git checkout "


def checkout_and_detect_on_windows(repository_path):
    powershell_path = r""  # The path of Windows powershell
    jar = r""  # The path of jnose-core-modified.jar
    repo = Repo(repository_path)
    git = repo.git

    target_repo_name = Util.get_repository_name_from_path(repository_path)
    smell_detection_folder = Util.get_smell_detection_results_folder(target_repo_name)
    commits = Util.get_all_sha(target_repo_name)

    try:
        os.makedirs(smell_detection_folder)
    except FileExistsError:
        print("Directory exists.")

    for sha in commits:
        commit = repo.commit(sha)
        command = powershell_path + " java -jar " + jar + " " + repository_path + " " + str(
            commit.committed_date) + " " + commit.hexsha + " " + smell_detection_folder
        print(CHECKOUT_COMMAND + commit.hexsha)
        git.checkout(commit.hexsha, '-f')
        os.system(command)


def checkout_and_detect_on_linux(repository_path):
    jar = r"./Detection/jnose-core-modified.jar"
    repo = Repo(repository_path)
    git = repo.git

    target_repo_name = Util.get_repository_name_from_path(repository_path)
    smell_detection_folder = Util.get_smell_detection_results_folder(target_repo_name)
    commits = Util.get_all_sha(target_repo_name)

    try:
        os.makedirs(smell_detection_folder)
    except FileExistsError:
        print("Directory exists.")

    for sha in commits:
        commit = repo.commit(sha)
        command = "java -jar " + jar + " " + repository_path + " " + str(
            commit.committed_date) + " " + commit.hexsha + " " + smell_detection_folder
        print(CHECKOUT_COMMAND + commit.hexsha)
        git.checkout(commit.hexsha, '-f')
        os.system(command)
