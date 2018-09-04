"""
Reads an csv file and repeats the first data line X amount of times
with each line having a different id value.

"""
import sys
import uuid

USAGE = """
Generates a fake csv file.
The first line is the headers line
Expects the data line to be the second line of the file, and without a member id value. The generated member_id will
prepend to the beginning of the line.


Usage:   ./generate_csv_file_util.py <csv_file> <num_copies> <output_filename>
Example: ./generate_csv_file_util.py /abs/path/to/file.csv 100 file-100.csv

"""


def generate_member_id():
    return str(uuid.uuid4())[:13]


def repeat_data_line(filename, num_copies, output_filename):
    headers = None
    data = None
    with open(filename, 'r') as csv_file:
        headers = csv_file.readline()
        data = csv_file.readline()

    with open(output_filename, 'w+') as output_file:
        output_file.write(headers)
        for _ in range(int(num_copies)):
            csv_line = '{}{}'.format(generate_member_id(), data)
            output_file.write(csv_line)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise RuntimeError("Must supply 3 arguments!\n{}".format(USAGE))
    repeat_data_line(sys.argv[1], sys.argv[2], sys.argv[3])
