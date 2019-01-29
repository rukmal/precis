from types import SimpleNamespace
import argparse
import sys


def main():
    args_parsed = buildArgparse()


def buildArgparse() -> SimpleNamespace:
    parser = argparse.ArgumentParser(
        prog='precis',
        description='The non-redundant resume engine'
    )

    # Required arguments
    parser.add_argument('data_file', action='store', nargs=1,
                        help='Data file to be used for resume')  # data file
    parser.add_argument('template_file', action='store', nargs=1,
                        help='Template file to be compiled')  # template file

    # Optional argument - overriding data
    parser.add_argument('--override', action='append', nargs='+',
                        help='File to be used to override main data file')

    print(parser.parse_args())

    return parser.parse_args()


if __name__ == '__main__':
    main()
