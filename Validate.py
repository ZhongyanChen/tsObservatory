import json
import csv
import os
from Util import Util
import argparse

'''
evolution data(commit) = sum of intro + removal in delta smell data
not removed count = evo chart's last commit's count
number of rows in removal time csv = total count of intro in delta smell data
Not removed count = intro - removed in delta count
'''


def validate_delta_smell_data_by_smell(evolution_data_file, delta_smell_data_file, smell_type):
    evolution_data = json.load(open(evolution_data_file))
    delta_smell_data = json.load(open(delta_smell_data_file))

    for i in range(0, len(evolution_data[smell_type])):
        current_instance_count = sum(delta_smell_data[smell_type][0][:i + 1]) + sum(
            delta_smell_data[smell_type][1][:i + 1])
        if current_instance_count != evolution_data[smell_type][i]:
            print(current_instance_count)
            print(evolution_data[smell_type][i])
            print(evolution_data['SHAs'][i])


def validate_delta_smell_data_by_repo(repository_name):
    evolution_data_file = os.path.join(Util.get_graph_data_folder(repository_name),
                                       repository_name + "_evolution_data.json")

    for key in Util.get_test_smells().keys():
        delta_smell_data_file = os.path.join(Util.get_graph_data_folder(repository_name),
                                             repository_name + "_delta_smell_data_" + key + ".json")
        validate_delta_smell_data_by_smell(evolution_data_file, delta_smell_data_file, key)


def validate_removal_time_by_smell(removal_time_data_file, delta_smell_data_file, smell_type):
    delta_smell_data = json.load(open(delta_smell_data_file))

    with open(removal_time_data_file, 'r', newline='') as csvfile:
        spamreader = csv.reader(csvfile)

        removal_count = 0
        survival_count = 0
        for row in spamreader:
            if row[2] != "inf":
                removal_count += 1
            else:
                survival_count += 1

    if removal_count != abs(sum(delta_smell_data[smell_type][1])):
        print(removal_count)
        print(sum(delta_smell_data[smell_type][1]))
        print(smell_type)

    if survival_count != sum(delta_smell_data[smell_type][0]) + sum(delta_smell_data[smell_type][1]):
        print(survival_count)
        print(sum(delta_smell_data[smell_type][0]) + sum(delta_smell_data[smell_type][1]))
        print(smell_type)
    ''''''


def validate_removal_time_by_repo(repository_name):
    for key in Util.get_test_smells().keys():
        removal_time_data_file = os.path.join(Util.get_graph_data_folder(repository_name),
                                              repository_name + "_removal_time_" + key + ".csv")
        delta_smell_data_file = os.path.join(Util.get_graph_data_folder(repository_name),
                                             repository_name + "_delta_smell_data_" + key + ".json")

        validate_removal_time_by_smell(removal_time_data_file, delta_smell_data_file, key)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("repository_name")
    args = parser.parse_args()

    validate_delta_smell_data_by_repo(args.repository_name)
    validate_removal_time_by_repo(args.repository_name)
