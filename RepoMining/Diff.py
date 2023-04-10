from git import Repo
import re
import os
import json
from Util import Util


# This class parses git diff message of two given commits
class Diff:
    def __init__(self, repository_path, sha_old, sha_new):
        self.repo = Repo(repository_path)
        self.sha_old = self.repo.commit(sha_old)
        self.sha_new = self.repo.commit(sha_new)
        self.git = self.repo.git

    # Check if a diff message of given commits is empty
    # Currently, it is not called by any scripts
    def check_if_no_change(self):
        diff = self.git.diff(self.sha_old, self.sha_new)

        is_empty = False

        if diff == "":
            is_empty = True
        else:
            pass

        return is_empty

    # This function parses the output of git diff --name-status
    # to get changed files' paths between two commits
    def get_changed_file_list(self):
        diff = self.git.diff(self.sha_old, self.sha_new, "--name-status")
        diff_lines = diff.split('\n')
        file_list = []

        for line in diff_lines:

            if "R" in line[0]:  # Renamed files
                file_list.append((line.split('\t')[1], line.split('\t')[2]))
            if "M" in line[0]:  # Modified files
                file_list.append((line.split('\t')[1], line.split('\t')[1]))
            if "A" in line[0]:  # Added files
                file_list.append(("", line.split('\t')[1]))
            if "D" in line[0]:  # Deleted files
                file_list.append((line.split('\t')[1], ""))
            if line[0] in ["C", "T", "U", "X",  "B"]:
                Exception("There are other types of changes in diff that we don't handle yet!")

        return file_list

    # This function computes the old-new commits file line number mapping.
    # It takes a git diff message of all contents of a file,
    # and returns [old line nums, new line nums].
    # For renamed files without changes, old line nums and new line nums will be empty lists.
    @staticmethod
    def get_line_num_diff(code_block):
        old_line_num_list = []
        new_line_num_list = []

        old_line_num = 1
        new_line_num = 1

        for line in code_block:

            # Unchanged lines
            if ' ' in line[0]:
                old_line_num_list.append(old_line_num)
                new_line_num_list.append(new_line_num)
                old_line_num += 1
                new_line_num += 1

            # Added lines
            if '+' in line[0]:
                old_line_num_list.append(None)
                new_line_num_list.append(new_line_num)
                new_line_num += 1

            # Deleted lines
            if '-' in line[0]:
                old_line_num_list.append(old_line_num)
                new_line_num_list.append(None)
                old_line_num += 1

        return [old_line_num_list, new_line_num_list]

    # This function parse the output of git diff --unified=99999
    # to get line number mappings of files between two given commits
    # Attention: it can only map files that are less than 99999 lines
    def map_line_num(self, changed_files_list):
        diff = self.git.diff(self.sha_old, self.sha_new, "--unified=99999")
        diff_lines = diff.split('\n')
        line_num_mapping = {}

        header_index = 0
        code_blocks = []
        for index in range(1, len(diff_lines)):
            # The header of a file in the diff message
            if re.match(r"@@ [-]([0-9]+),[0-9]+\s[+]([0-9]+),[0-9]+ @@", diff_lines[index]):
                header_index = index + 1

            # This line will only appear for renamed files without changes
            if diff_lines[index] == "similarity index 100%":
                header_index = index

            # Beginning of a new file's diff
            if "diff --git" in diff_lines[index]:
                diff_git_index = index
                code_blocks.append(diff_lines[header_index: diff_git_index])

            # The last line of the diff message
            if index == (len(diff_lines) - 1):
                code_blocks.append(diff_lines[header_index: len(diff_lines)])

        # Adding line num mappings to output
        for i in range(0, len(code_blocks)):
            line_num_diff = self.get_line_num_diff(code_blocks[i])
            line_num_mapping.update({str(changed_files_list[i]): {"Old_lines": line_num_diff[0],
                                                                  "New_lines": line_num_diff[1]}})

        return line_num_mapping


# This function writes line number mapping of two given commits into a json file
def write_mapping(destination_folder, old_sha, new_sha, line_num_mapping_dict):
    raw_data_file_name = old_sha + ".." + new_sha + ".json"
    raw_data_file_path = os.path.join(destination_folder, raw_data_file_name)

    with open(raw_data_file_path, "w") as outfile:
        json.dump(line_num_mapping_dict, outfile)

    print(raw_data_file_path + " is created!")


def get_line_mappings(repository_path):
    target_repo_name = Util.get_repository_name_from_path(repository_path)
    diff_folder = Util.get_diff_folder(target_repo_name)

    try:
        os.makedirs(diff_folder)
    except FileExistsError:
        print("Directory exists")

    commits = Util.get_all_sha(target_repo_name, dictionary=False)

    temp_sha = commits[0]

    for j in range(1, len(commits)):
        diff_obj = Diff(repository_path, temp_sha, commits[j])
        changed_files = diff_obj.get_changed_file_list()
        mapping = diff_obj.map_line_num(changed_files)
        write_mapping(diff_folder, temp_sha, commits[j], mapping)
        temp_sha = commits[j]
