import argparse
from Analysis import get_evolution_data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Positional arguments
    parser.add_argument("repository_name")
    args = parser.parse_args()

    get_evolution_data(args.repository_name)
