#!/opt/homebrew/bin/python3.11
import os
import argparse
import matplotlib.pyplot as plt
import csv
from datetime import datetime
from collections import defaultdict

WORKDIR="../results/memory"
FIGDIR="figures"

def parse_csv(filename):

    dates = []
    memory_kb = []
    with open(filename, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            # Parse date string and convert to datetime object
            date_str = row['date']
            date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')

            # Append data to lists
            dates.append(date_obj)
            if len(row['memory_kb']) > 0:
                memory_kb.append(int(row['memory_kb']))
    return memory_kb


def iterate_files(workdir, data):
    # list file and iterate through workdir and check if cpu is in filename
    for filename in os.listdir(workdir):
        if "memory" in filename:
            data[filename.replace(".csv", "")] = parse_csv(os.path.join(workdir, filename))

def uniform(data):
    max_length = 0
    for v in data.values():
        max_length = max(max_length, len(v))

    # Pad the shorter lists with zeros
    for v in data.values():
        v += [0] * (max_length - len(v))

def plot(args, data):
    plt.figure(figsize=(6, 3))
    for k,v in data.items():
        plt.plot(v, label=k.replace("memory_", " ").title().replace("_Ksm", "(+KSM)"))

    plt.yscale('log')
    plt.xlabel('Time [s]')
    plt.ylabel('Memory Usage [KB]')
    plt.title('Memory Usage Over Time')
    plt.legend()
    plt.grid()
    plt.tight_layout()

    if args.save:
        plt.savefig(os.path.join(FIGDIR,"memory.pdf"))
        print(f"Figure saved to {os.path.join(FIGDIR,'memory.pdf')}")
    if args.show:
        plt.show()

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", type=str, default=WORKDIR, help="Path to the workdir")
    parser.add_argument("--show", required=False, default=False, action="store_true", help="Display plot")
    parser.add_argument("--save", required=False, default=True, action="store_true", help="Save plot to pdf")
    args = parser.parse_args()
    
    data = defaultdict(list)
    
    iterate_files(args.workdir, data)
    # uniform(data)
    plot(args, data)

if __name__ == "__main__":
    main()