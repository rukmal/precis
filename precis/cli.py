import argparse


def main():
    parser = argparse.ArgumentParser(
        prog='precis',
        description='The non-redundant resume engine.'
    )

    # Required arguments
    parser.add_argument('data_file', action='store', nargs=1,
                        help='Data file to be used for resume. Must be in \
                        Precis-compatible format.')  # data file
    parser.add_argument('template_file', action='store', nargs=1,
                        help='Template file to be compiled.')  # template file

    # Optional argument - overriding data
    parser.add_argument('--override', action='append', nargs='+',
                        help='File(s) to be used to override main data file. \
                        In ascending order of specificity; i.e. data_file < \
                        override 1 < override 2 < ... < override n.')

    args = parser.parse_args()

    print(args.data_file)

if __name__ == '__main__':
    main()
