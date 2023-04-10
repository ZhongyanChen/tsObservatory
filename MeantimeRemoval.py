import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import math
import argparse
import MapSmellInstance
import csv
from Util import Util


class SmellInstancesLife:
    def __init__(self):
        self.instances = []
        self.introduction_times = []
        self.removed_times = []

    def update_all_instances(self, removed_instances, mapping_data):
        for i in range(0, len(self.instances)):
            # Only update the keys of not yet removed smell instances
            if (self.removed_times[i] == math.inf) and (self.instances[i] not in removed_instances):
                self.instances[i] = MapSmellInstance.map_new_record(self.instances[i], mapping_data, empty_path_override=True)

    def insert_new_instance(self, new_instance, committed_date):
        self.instances.append(new_instance)
        self.introduction_times.append(committed_date)
        self.removed_times.append(math.inf)

    def update_removal_time(self, row, committed_date):
        for i in range(0, len(self.instances)):
            # Only update smell instances not having a removal time yet
            if (self.instances[i] == row) and (self.removed_times[i] == math.inf):
                self.removed_times[i] = committed_date
                break

    def get_instances(self):
        return self.instances

    def get_introduction_times(self):
        return self.introduction_times

    def get_removal_times(self):
        return self.removed_times

    def get_inf(self):
        count = 0
        for time in self.removed_times:
            if time == math.inf:
                count += 1
        return count


def map_current_instances(current_instances, mapping_data):
    mapped_instances = []

    for row in current_instances:
        mapped_instances.append(MapSmellInstance.map_new_record(row, mapping_data, empty_path_override=True))

    return mapped_instances


def get_introduction_commits(mapped_current_instances, smell_instances_new_commit, smell_instance_life, committed_date):
    for row in smell_instances_new_commit:
        if row not in mapped_current_instances:
            smell_instance_life.insert_new_instance(row, committed_date)


def get_removed_instances(current_instances, mapped_current_instances, smell_instances_new_commit):
    removed_instances = []
    for index in range(0, len(mapped_current_instances)):
        if mapped_current_instances[index] not in smell_instances_new_commit:
            removed_instances.append(current_instances[index])

    return removed_instances


def get_data(smell_detection_result_paths, diff_data_folder, smell_instances_life, smell_type):
    current_instances = {"SHA": "", "Instances": []}

    current_csv_path = smell_detection_result_paths[0]

    # All smell instance from the initial target commit are introduced in this commit, so they are all collected.
    get_introduction_commits(current_instances['Instances'], Util.read_csv_by_smell(current_csv_path, smell_type, sort=True),
                             smell_instances_life, Util.get_committed_time_from_file_path(current_csv_path))

    # Initializing current_instances
    current_instances['SHA'] = Util.get_sha_from_file_path(current_csv_path)
    current_instances['Instances'] = Util.read_csv_by_smell(current_csv_path, smell_type, sort=True)

    for result_path in smell_detection_result_paths[1:]:
        diff_file = current_instances['SHA'] + ".." + Util.get_sha_from_file_path(result_path) + ".json"
        diff_path = os.path.join(diff_data_folder, diff_file)
        diff_data = MapSmellInstance.load_line_mapping_data(diff_path)
        next_commit_result = Util.read_csv_by_smell(result_path, smell_type, sort=True)

        mapped_current_instances = map_current_instances(current_instances['Instances'], diff_data)
        # Forecast instances that will be removed in the next commit
        removed_instances = get_removed_instances(current_instances['Instances'], mapped_current_instances,
                                                  next_commit_result)

        # Only update instances that are not removed
        smell_instances_life.update_all_instances(removed_instances, diff_data)

        # Get the intro/removal time here
        # May have to handle removal first
        for instance in removed_instances:
            smell_instances_life.update_removal_time(instance, Util.get_committed_time_from_file_path(result_path))

        get_introduction_commits(mapped_current_instances, next_commit_result,
                                 smell_instances_life, Util.get_committed_time_from_file_path(result_path))
        # get_removal_commits(mapped_current_instances, current_result, smell_instances_life, get_committed_date_from_file_name(result))

        print("done!")
        ''''''
        if len(next_commit_result) != smell_instances_life.get_inf():
            for j in range(0, len(smell_instances_life.instances)):
                if smell_instances_life.removed_times[j] == math.inf:
                    if smell_instances_life.instances[j] not in next_commit_result:
                        print(smell_instances_life.instances[j])
                        print(smell_instances_life.introduction_times[j])

            print(smell_instances_life.get_inf())
            print(len(next_commit_result))
            print(os.path.basename(result_path))
            break

        current_instances['SHA'] = Util.get_sha_from_file_path(result_path)
        current_instances['Instances'] = next_commit_result

    return smell_instances_life.get_instances()


def write_data(repository_name, smell_instance_life_object, smell_type):
    destination_folder = Util.get_graph_data_folder(repository_name)
    raw_data_file_name = repository_name + "_removal_time_" + smell_type + ".csv"
    raw_data_file_path = os.path.join(destination_folder, raw_data_file_name)

    with open(raw_data_file_path, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile)
        for k in range(0, len(smell_instance_life_object.introduction_times)):
            spamwriter.writerow([smell_instance_life_object.instances[k],
                                 smell_instance_life_object.introduction_times[k],
                                 smell_instance_life_object.removed_times[k]])

    print(raw_data_file_path + " is created!")


def draw_stacked_bar_chart(repository_name, smells):
    removal_time_zone_data = [["Less than 24 hours"], ["1-7 days"], ["8-30days"], ["31-365 days"], ["More than a year"],
                              ["Not removed"]]
    columns = ["Test Smells"]
    graph_data_folder = Util.get_graph_data_folder(repository_name)

    for test_smell in smells.keys():

        file_name = repository_name + "_removal_time_" + test_smell + ".csv"
        columns.append(test_smell)
        current_smell_data = [0, 0, 0, 0, 0, 0]

        with open(os.path.join(graph_data_folder, file_name), 'r') as csvfile:
            spamreader = csv.reader(csvfile)

            for smell_instance in spamreader:
                if smell_instance[2] == "inf":
                    current_smell_data[5] += 1
                else:
                    removal_hour = ((int(smell_instance[2]) - int(smell_instance[1])) / 3600)

                    if removal_hour < 24.00:
                        current_smell_data[0] += 1

                    if 24.00 <= removal_hour < 168.00:
                        current_smell_data[1] += 1

                    if 168.00 <= removal_hour < 720.00:
                        current_smell_data[2] += 1

                    if 720.00 <= removal_hour < 8760.00:
                        current_smell_data[3] += 1

                    if 8760.00 <= removal_hour < math.inf:
                        current_smell_data[4] += 1

            for i in range(len(current_smell_data)):
                removal_time_zone_data[i].append(current_smell_data[i])

        print(removal_time_zone_data)
    df = pd.DataFrame(removal_time_zone_data, columns=columns)
    df.plot(x='Test Smells', kind='bar', stacked=True, title="Removal Time Zone Chart: " + repository_name)
    plt.show()


def calculate_mean_time_of_removal(total_time, counts):
    if counts != 0:
        return total_time / counts
    else:
        return 0


def draw_mean_time_of_removal(repository_name, smells):
    mean_time_of_removal = []
    smell_types = []
    graph_data_folder = Util.get_graph_data_folder(repository_name)

    for test_smell in smells.keys():

        total_removal_time = 0
        count = 0

        file_name = repository_name + "_removal_time_" + test_smell + ".csv"

        smell_types.append(test_smell)
        with open(os.path.join(graph_data_folder, file_name), 'r') as csvfile:
            spamreader = csv.reader(csvfile)

            for smell_instance in spamreader:
                if smell_instance[2] != "inf":
                    total_removal_time += (int(smell_instance[2]) - int(smell_instance[1]))
                    count += 1
        print(test_smell)
        print(total_removal_time)
        print(count)
        mean_time_of_removal.append(calculate_mean_time_of_removal(total_removal_time, count) / 3600)
    print(mean_time_of_removal)
    plt.bar(smell_types, mean_time_of_removal)
    plt.ylabel('Hours')
    plt.xlabel('Test smells')
    plt.xticks(rotation=45)
    plt.title('Mean Time of Removal Chart: ' + repository_name)
    plt.show()


def draw_removal_times_boxplot(repository_name, smells):
    columns = []
    rows = []
    graph_data_folder = Util.get_graph_data_folder(repository_name)

    for test_smell in smells.keys():

        rows.append(test_smell)
        removal_time_data = []

        file_name = repository_name + "_removal_time_" + test_smell + ".csv"

        with open(os.path.join(graph_data_folder, file_name), 'r') as csvfile:
            spamreader = csv.reader(csvfile)

            for smell_instance in spamreader:
                if smell_instance[2] != "inf":
                    removal_time = (int(smell_instance[2]) - int(smell_instance[1]))
                    removal_time_data.append(removal_time / 3600)

        columns.append(removal_time_data)

    x_pos = np.arange(start=1, stop=len(rows) + 1)
    plt.boxplot(columns)
    plt.xticks(x_pos, rows, rotation=45)
    plt.ylabel('Hours')
    plt.xlabel('Test smells')
    plt.title('Removal Times Boxplot: ' + repository_name)
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Positional arguments
    parser.add_argument("repository_name")

    args = parser.parse_args()

    diff_folder = Util.get_diff_folder(args.repository_name)
    smell_detection_files = Util.get_all_smell_detection_result_paths(Util.get_all_sha(args.repository_name, dictionary=False),
                                                                      Util.get_smell_detection_results_folder(args.repository_name))
    test_smells = Util.get_test_smells()
    ''''''
    for smell in test_smells.keys():
        sl = SmellInstancesLife()
        get_data(smell_detection_files, diff_folder, sl, smell)
        write_data(args.repository_name, sl, smell)

    #draw_mean_time_of_removal(args.repository_name, test_smells)
    #draw_removal_times_boxplot(args.repository_name, test_smells)
    #draw_stacked_bar_chart(args.repository_name, test_smells)
