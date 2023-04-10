import argparse
from Detection import get_target_sha
from Detection import checkout_and_detect_on_windows
from Detection import checkout_and_detect_on_linux


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Positional arguments
    parser.add_argument("repository_path")
    parser.add_argument("index", type=int)
    args = parser.parse_args()

    get_target_sha(args.repository_path, args.index)
    checkout_and_detect_on_windows(args.repository_path)
    #checkout_and_detect_on_linux(args.repository_path)
