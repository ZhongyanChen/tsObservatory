import argparse
from RepoMining import get_test_growth
from RepoMining import get_line_mappings


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Positional argument
    parser.add_argument("repository_path")
    args = parser.parse_args()

    get_test_growth(args.repository_path)
    get_line_mappings(args.repository_path)
