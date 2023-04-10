import matplotlib.pyplot as plt
import os
from matplotlib.pyplot import MultipleLocator
import csv
import json
from Util import Util


def get_data_per_smell(smell_detection_result_paths, smell_name):
    smell_instances_count = []

    for result in smell_detection_result_paths:
        smell_data = Util.read_csv_by_smell(result, smell_name, sort=False)
        row_count = len(smell_data)
        smell_instances_count.append(row_count)

    return smell_instances_count


# get data of the x-axis and the y-axis of test loc
def get_test_data(test_data_path):
    commits = []
    test_loc = []

    with open(test_data_path, 'r') as test_data_file:
        spamreader = csv.reader(test_data_file)

        for row in spamreader:
            commits.append(row[0])
            test_loc.append(int(row[1]))

    return [commits, test_loc]


def get_raw_data(smell_types, smell_detection_result_paths, test_growth_data):
    data = {}

    for key in smell_types.keys():
        data.update({key: get_data_per_smell(smell_detection_result_paths, smell_types[key])})

    data.update({"SHAs": test_growth_data[0]})
    data.update({"Test Growth": test_growth_data[1]})

    return data


def write_raw_data(data, repository_name):
    destination_folder = Util.get_graph_data_folder(repository_name)

    raw_data_file_name = repository_name + "_evolution_data.json"
    raw_data_file_path = os.path.join(destination_folder, raw_data_file_name)

    with open(raw_data_file_path, "w") as outfile:
        json.dump(data, outfile)

    print(raw_data_file_path + " is created!")


# Producing evolution charts with smell data only
def draw_smell_evolution_charts(data, repository_name, smell_type):
    chart_name = "The evolution chart of " + repository_name
    destination_folder = Util.get_graph_data_folder(repository_name)
    graph_path = os.path.join(destination_folder, chart_name + ".png")
    counter = 1  # Counts how many types of smells are processed

    for smell_type in smell_type.keys():

        if counter <= 10:  # 10 is the maximum number of default colors supported by matplotlib
            plt.plot(data['SHAs'], data[smell_type], marker='.', label=smell_type)
            counter += 1
        else:
            plt.plot(data['SHAs'], data[smell_type], marker='2', label=smell_type)
            counter += 1

    plt.title(chart_name)
    plt.xlabel("Commits containing changes to test code")
    plt.ylabel("Number of smell instances")
    plt.legend()
    plt.show()
    # plt.savefig(graph_path)


# Producing evolution charts with a type of smell data and lines of test code data
def draw_evolution_charts(data, repository_name, smell_type):
    chart_name = "The evolution chart of " + repository_name + " " + smell_type
    destination_folder = Util.get_graph_data_folder(repository_name)
    graph_path = os.path.join(destination_folder, chart_name + ".png")

    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('commits')
    ax1.set_ylabel('Number of smell instances', color=color)
    ax1.plot(data['SHAs'], data[smell_type], marker='.', color=color, label='AR')
    ax1.tick_params(axis='y', labelcolor=color)

    # instantiate a second axes that shares the same x-axis
    ax2 = ax1.twinx()

    color = 'tab:blue'
    ax2.set_ylabel('Lines of test code', color=color)  # we already handled the x-label with ax1
    ax2.plot(data['SHAs'], data['Test Growth'], marker='.', color=color, label='Lines of test code')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.yaxis.set_major_locator(MultipleLocator(2500))

    # fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.legend()
    plt.show()
    # plt.savefig(graph_path)


def get_evolution_data(repository_name):
    line_of_test_data_path = os.path.join(Util.get_graph_data_folder(repository_name),
                                          Util.get_test_growth_file_name(repository_name))

    smell_detection_files = Util.get_all_smell_detection_result_paths(Util.get_all_sha(repository_name),
                                                                      Util.get_smell_detection_results_folder(
                                                                          repository_name))

    test_data = get_test_data(line_of_test_data_path)

    raw_data = get_raw_data(Util.get_test_smells(), smell_detection_files, test_data)
    write_raw_data(raw_data, repository_name)


'''
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Positional arguments
    parser.add_argument("repository_name")

    # Optional arguments
    
    parser.add_argument("-t", "--total", help="produce an evolution chart for smell instances in total",
                        action="store_true")
    
    parser.add_argument("-a", "--all", help="produce an evolution chart for instances of every smell",
                        action="store_true")
    parser.add_argument("-AR", help="produce an evolution chart for assertion roulette instances",
                        action="store_true")
    parser.add_argument("-CTL", help="produce an evolution chart for conditional test logic instances",
                        action="store_true")
    parser.add_argument("-CI", help="produce an evolution chart for constructor initialization instances",
                        action="store_true")
    parser.add_argument("-DT", help="produce an evolution chart for default test instances",
                        action="store_true")
    parser.add_argument("-DA", help="produce an evolution chart for duplicate assert instances",
                        action="store_true")
    parser.add_argument("-ET", help="produce an evolution chart for eager test instances",
                        action="store_true")
    parser.add_argument("-EptT", help="produce an evolution chart for empty test instances",
                        action="store_true")
    parser.add_argument("-EH", help="produce an evolution chart for exception handling instances",
                        action="store_true")
    parser.add_argument("-GF", help="produce an evolution chart for general fixture instances",
                        action="store_true")
    parser.add_argument("-IT", help="produce an evolution chart for ignored test instances",
                        action="store_true")
    parser.add_argument("-LT", help="produce an evolution chart for lazy test instances",
                        action="store_true")
    parser.add_argument("-MNT", help="produce an evolution chart for magic number test instances",
                        action="store_true")
    parser.add_argument("-MG", help="produce an evolution chart for mystery guest instances",
                        action="store_true")
    parser.add_argument("-RP", help="produce an evolution chart for redundant print instances",
                        action="store_true")
    parser.add_argument("-RA", help="produce an evolution chart for redundant assertion instances",
                        action="store_true")
    parser.add_argument("-RO", help="produce an evolution chart for resource optimism instances",
                        action="store_true")
    parser.add_argument("-SE", help="produce an evolution chart for sensitive equality instances",
                        action="store_true")
    parser.add_argument("-ST", help="produce an evolution chart for sleepy test instances",
                        action="store_true")
    parser.add_argument("-UT", help="produce an evolution chart for unknown test instances",
                        action="store_true")
    args = parser.parse_args()

    line_of_test_data_path = os.path.join(Util.get_graph_data_folder(args.repository_name),
                                          Util.get_test_growth_file_name(args.repository_name))

    smell_detection_data_folder = Util.get_smell_detection_results_folder(args.repository_name)
    smell_detection_files = Util.get_all_smell_detection_result_paths(Util.get_all_sha(args.repository_name),
                                                                      Util.get_smell_detection_results_folder(
                                                                          args.repository_name))

    test_data = get_test_data(line_of_test_data_path)

    raw_data = get_raw_data(Util.get_test_smells(), smell_detection_files, test_data)
    write_raw_data(raw_data, args.repository_name)

    if args.total:
        smell_graph_data = get_smell_data(args.smell_graph_data)
        test_graph_data = get_test_data(args.test_graph_data)
        draw_evolution_charts(test_graph_data[0], smell_graph_data, test_graph_data[1])
    
    if args.all:
        draw_smell_evolution_charts(raw_data, args.repository_name, Util.get_test_smells())

    if args.AR:
        draw_evolution_charts(raw_data, args.repository_name, "Assertion Roulette")

    if args.CTL:
        draw_evolution_charts(raw_data, args.repository_name, "Conditional Test Logic")

    if args.CI:
        draw_evolution_charts(raw_data, args.repository_name, "Constructor Initialization")

    if args.DT:
        draw_evolution_charts(raw_data, args.repository_name, "Default Test")

    if args.DA:
        draw_evolution_charts(raw_data, args.repository_name, "Duplicate Assert")

    if args.ET:
        draw_evolution_charts(raw_data, args.repository_name, "Eager Test")

    if args.EptT:
        draw_evolution_charts(raw_data, args.repository_name, "Empty Test")

    if args.EH:
        draw_evolution_charts(raw_data, args.repository_name, "Exception Handling")

    if args.GF:
        draw_evolution_charts(raw_data, args.repository_name, "General Fixture")

    if args.IT:
        draw_evolution_charts(raw_data, args.repository_name, "Ignored Test")

    if args.LT:
        draw_evolution_charts(raw_data, args.repository_name, "Lazy Test")

    if args.MNT:
        draw_evolution_charts(raw_data, args.repository_name, "Magic Number Test")

    if args.MG:
        draw_evolution_charts(raw_data, args.repository_name, "Mystery Guest")

    if args.RP:
        draw_evolution_charts(raw_data, args.repository_name, "Redundant Print")

    if args.RA:
        draw_evolution_charts(raw_data, args.repository_name, "Redundant Assertion")

    if args.RO:
        draw_evolution_charts(raw_data, args.repository_name, "Resource Optimism")

    if args.SE:
        draw_evolution_charts(raw_data, args.repository_name, "Sensitive Equality")

    if args.ST:
        draw_evolution_charts(raw_data, args.repository_name, "Sleepy Test")

    if args.UT:
        draw_evolution_charts(raw_data, args.repository_name, "Unknown Test")
'''