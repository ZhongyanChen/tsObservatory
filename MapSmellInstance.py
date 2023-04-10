import re
from pathlib import Path
import json
import ast


def load_line_mapping_data(diff_data_file_path):
    mapping_data = {}

    with open(diff_data_file_path, 'r') as f:
        raw_data = json.load(f)

    for key in raw_data.keys():
        # Parse key strings to (Path(old_path), Path(new_path)) tuples
        key_tuple = ()
        for path in ast.literal_eval(key):
            key_tuple += (Path(path),)

        mapping_data.update({key_tuple: raw_data[key]})

    return mapping_data


def update_file_path(filepath, mapping_data):
    updated_file_path = filepath
    if filepath == "":
        pass
    else:
        for key in mapping_data.keys():

            # If this code block is never executed in the loop, filepath is not in the diff message,
            # so filepath has not changed between these two commits
            if Path(filepath) == Path(key[0]):
                updated_file_path = key[1]
                break

    return Path(updated_file_path)


# This function get parse all line numbers in a smell detection result
# from string to integer
def get_line_numbers(line_num_cell):
    raw_numbers = [int(number) for number in re.findall(r"\d+", line_num_cell)]

    # For line numbers like 110-110 or 110-120
    if re.match(r"[0-9]+\-[0-9]+", line_num_cell):
        line_numbers = list(range(min(raw_numbers), max(raw_numbers) + 1))
    else:  # For line numbers like 110 or 110,112,115
        line_numbers = raw_numbers

    return line_numbers


# Update given line numbers in the old commit to new commit
def update_line_numbers(line_numbers, line_num_mapping):
    updated_line_numbers = []

    # This is for renamed file without changes
    if len(line_num_mapping['Old_lines']) == 0 and len(line_num_mapping['New_lines']) == 0:
        updated_line_numbers = line_numbers
    else:
        for line_num in line_numbers:
            if line_num in line_num_mapping['Old_lines']:
                updated_line_numbers.append(line_num_mapping['New_lines'][line_num_mapping['Old_lines'].index(line_num)])

    return updated_line_numbers


# Map test file path, production file path, line numbers in a row of smell detection result
# from old commit to new commit
def map_new_record(old_row, mapping_data, empty_path_override=False):
    old_test_path = Path(old_row[0])
    new_test_path = update_file_path(old_row[0], mapping_data)
    new_production_file_path = update_file_path(old_row[1], mapping_data)

    # Check if the test path of this smell instance has changed in this diff.
    # If not, no need to map line numbers
    if (old_test_path, new_test_path) in mapping_data.keys():
        line_num_mapping = mapping_data[(old_test_path, new_test_path)]

        #temp_line_nums = update_line_numbers(get_line_numbers(old_row[4]), line_num_mapping)
        temp_line_nums = update_line_numbers(old_row[4], line_num_mapping)
    else:
        temp_line_nums = old_row[4]

    if None not in temp_line_nums:
        new_line_nums = sorted(temp_line_nums)
    else:
        new_line_nums = temp_line_nums

    if empty_path_override:
        if new_production_file_path == Path(""):
            new_production_file_path = ""
        return [new_test_path.__str__(), new_production_file_path.__str__(), old_row[2], old_row[3], new_line_nums]
    else:
        return [new_test_path.__str__(), new_production_file_path.__str__(), old_row[2], old_row[3], new_line_nums]


def match(mapped_old_row, new_row):
    #processed_new_row = [Path(new_row[0]), Path(new_row[1]), new_row[2], new_row[3], sorted(get_line_numbers(new_row[4]))]
    processed_new_row = [Path(new_row[0]).__str__(), Path(new_row[1]).__str__(), new_row[2], new_row[3], new_row[4]]

    if mapped_old_row == processed_new_row:
        return True
    else:
        return False


def get_unchanged_smell_instance_count(old_smell_detection_results, new_smell_detection_results, mapping_data):

    unchanged_instance = 0

    for row in old_smell_detection_results:

        prediction = map_new_record(row, mapping_data)

        for row2 in new_smell_detection_results:

            if match(prediction, row2):
                unchanged_instance += 1
                break

    return unchanged_instance
