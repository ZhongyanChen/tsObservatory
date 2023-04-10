import numpy as np
import matplotlib.pyplot as plt
import os
import MapSmellInstance
import argparse
import json
from Util import Util


def get_smell_intro_removal(new_csv_path, smell_type, old_csv_path=None, diff_file_path=None):

    if old_csv_path is None:
        new_smell_instances = Util.read_csv_by_smell(new_csv_path, smell_type)
        introduction = len(new_smell_instances)
        removal = 0

    else:
        diff_data = MapSmellInstance.load_line_mapping_data(diff_file_path)
        old_smell_instances = Util.read_csv_by_smell(old_csv_path, smell_type)
        new_smell_instances = Util.read_csv_by_smell(new_csv_path, smell_type)

        unchanged_smell_instance_count = MapSmellInstance.get_unchanged_smell_instance_count(old_smell_instances,
                                                                                             new_smell_instances,
                                                                                             diff_data)
        introduction = len(new_smell_instances) - unchanged_smell_instance_count
        removal = -(len(old_smell_instances) - unchanged_smell_instance_count)

    return [introduction, removal]


def get_data_by_smell(smell_detection_result_paths, diff_data_folder, smell_type):

    data = [[], []]
    current_csv_path = smell_detection_result_paths[0]
    current_intro_removal_data = get_smell_intro_removal(current_csv_path, smell_type)

    data[0].append(current_intro_removal_data[0])
    data[1].append(current_intro_removal_data[1])

    for result in smell_detection_result_paths[1:]:
        diff_file = Util.get_diff_file_name(current_csv_path, result)
        diff_path = os.path.join(diff_data_folder, diff_file)

        current_intro_removal_data = get_smell_intro_removal(result, smell_type, current_csv_path, diff_path)

        data[0].append(current_intro_removal_data[0])
        data[1].append(current_intro_removal_data[1])
        current_csv_path = result
        print("done!")

    print(smell_type + " analysis complete!")
    return {smell_type: data}


def get_delta_smell_chart_data(smell_detection_result_paths, diff_data_folder, test_smell_set):
    chart_data = {}

    for smell in test_smell_set:
        chart_data.update(get_data_by_smell(smell_detection_result_paths, diff_data_folder, smell))

    chart_data.update(Util.get_all_sha(os.path.basename(diff_data_folder), dictionary=True))

    return chart_data


def write_data(data, repository_name):
    destination_folder = Util.get_graph_data_folder(repository_name)

    try:
        os.makedirs(destination_folder)
    except FileExistsError:
        print("Directory exists")

    raw_data_file_name = repository_name + "_delta_smell_data.json"
    raw_data_file_path = os.path.join(destination_folder, raw_data_file_name)

    with open(raw_data_file_path, "w") as outfile:
        json.dump(data, outfile)

    print(raw_data_file_path + " is created!")


def get_delta_smell_data_by_smell(smell_detection_result_paths, diff_data_folder, smell_type):
    chart_data = {}

    chart_data.update(get_data_by_smell(smell_detection_result_paths, diff_data_folder, smell_type))

    chart_data.update(Util.get_all_sha(os.path.basename(diff_data_folder), dictionary=True))

    return chart_data


def write_data_by_smell(data, repository_name, smell):
    destination_folder = Util.get_graph_data_folder(repository_name)

    try:
        os.makedirs(destination_folder)
    except FileExistsError:
        print("Directory exists")

    raw_data_file_name = repository_name + "_delta_smell_data_" + smell + ".json"
    raw_data_file_path = os.path.join(destination_folder, raw_data_file_name)

    with open(raw_data_file_path, "w") as outfile:
        json.dump(data, outfile)

    print(raw_data_file_path + " is created!")


def draw_delta_smell_chart(data, repository_name, smell_type):
    chart_name = "The Delta Smell Chart of " + repository_name + ": " + smell_type
    N = len(data['commits'])
    x = data['commits']

    ind = np.arange(N)
    # width = 0.35

    plt.bar(x, data[smell_type][0], label='Introduction')
    plt.bar(x, data[smell_type][1], label='Removal')

    plt.ylabel('Number of smell instances')
    plt.xlabel('commits')
    plt.title(chart_name)

    plt.legend(loc='best')
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Positional arguments
    parser.add_argument("repository_name")

    args = parser.parse_args()

    smell_detection_data_folder = Util.get_smell_detection_results_folder(args.repository_name)
    diff_folder = Util.get_diff_folder(args.repository_name)
    smell_detection_files = Util.get_all_smell_detection_result_paths(Util.get_all_sha(args.repository_name, dictionary=True)['commits'],
                                                                      smell_detection_data_folder)

    for test_smell in Util.get_test_smells().keys():
        smell_data = get_delta_smell_data_by_smell(smell_detection_files, diff_folder, test_smell)
        write_data_by_smell(smell_data, args.repository_name, test_smell)
    '''
    data_file = r""  # Path of the data file here
    data = json.load(open(data_file))
    draw_delta_smell_chart(data, args.repository_name, "Assertion Roulette")
    '''
