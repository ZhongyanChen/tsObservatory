import os
import pandas as pd
import csv
import Config
import argparse


def read_csv(csv_path):
    dataframe = pd.read_csv(csv_path, header=None, usecols=[0, 1, 2, 3, 4],
                            names=['test path', 'production code path', 'detected smell', 'method name',
                                   'line number'], keep_default_na=False)

    return dataframe


# This function finds all paths of smell detection result files and returns a list
def get_smell_detection_files(repository_name):

    smell_detection_folder = os.path.join(Config.get_smell_detection_path(), repository_name)
    smell_detection_results = os.listdir(smell_detection_folder)

    smell_detection_files = []
    for file in smell_detection_results:
        smell_detection_files.append(os.path.join(smell_detection_folder, file))

    return smell_detection_files


# This function finds all duplicated smell instances in a given smell detection file
def find_duplicates(smell_detection_file_path):

    dataframe = read_csv(smell_detection_file_path)
    rows = [[os.path.basename(smell_detection_file_path)]]

    for i in range(0, len(dataframe)):
        if dataframe.duplicated(keep=False)[i]:
            rows.append(dataframe.values.tolist()[i])

    rows.append(["===================================================================="])
    rows.append([""])

    return rows


# This function only produce output if there are non-Lazy-Test duplicated smell instances
def find_unexpected_duplicates(smell_detection_file_path):
    dataframe = read_csv(smell_detection_file_path)
    rows = [[os.path.basename(smell_detection_file_path)]]

    if dataframe.duplicated(keep=False).any():  # If duplicated instances exist in given smell detection file:
        df = dataframe[dataframe.duplicated(keep=False)]
        query = df.query("`detected smell` != 'Lazy Test'")
        if len(query) != 0:
            print(rows)
            for line in query.values.tolist():
                rows.append(line)
            rows.append(["===================================================================="])
            rows.append([""])
            return rows
        else:  # All duplicates are Lazy Test instances
            return []
    else:  # No duplicated instances in given smell detection file
        return []


# This function writes duplicated smell instances to a csv file
def write_duplicated_instances(repository_name, duplicated_instances_data):
    file_name = repository_name + "_duplicated_smell_instances.csv"
    file_path = os.path.join(Config.get_duplicated_instances_path(), file_name)

    try:
        os.makedirs(Config.get_duplicated_instances_path())
    except FileExistsError:
        print("Directory exists")

    with open(file_path, 'w', newline='') as f:
        spamwriter = csv.writer(f)

        for file in duplicated_instances_data:
            #spamwriter.writerows(find_duplicates(file))
            spamwriter.writerows(find_unexpected_duplicates(file))
            print(file +" is done!")

    print(file_name + " was created!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Positional arguments
    parser.add_argument("repository_name")

    args = parser.parse_args()

    files = get_smell_detection_files(args.repository_name)
    write_duplicated_instances(args.repository_name, files)
