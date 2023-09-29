#!/opt/homebrew/bin/python3.11
import os
import argparse
import matplotlib.pyplot as plt
from collections import defaultdict

WORKDIR="../results/cpu"
FIGDIR="figures"

def parse_file(filename):
    index = -1
    data_local = defaultdict(list)
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("Linux"):
                index += 1
                data_local[index].append(0)
            elif "all" in line:
                values = line.split()
                # 3: user, 5: system, 6: iowait
                data_local[index].append(float(values[3]) + float(values[5]) + float(values[6]))

    return data_local[0]

def iterate_files(workdir, data):
    # list file and iterate through workdir and check if cpu is in filename
    for filename in os.listdir(workdir):
        if "cpu" in filename:
            data[filename.replace(".txt", "")] = parse_file(os.path.join(workdir, filename))

def uniform(data):
    max_length = 0
    for v in data.values():
        max_length = max(max_length, len(v))

    # Pad the shorter lists with zeros
    for v in data.values():
        v += [0] * (max_length - len(v))
        
def plot(args, data):
    plt.figure(figsize=(6, 3))  # Adjust the figure size if needed
    for k,v in data.items():
        plt.plot(v, label=k.replace("_cpu", " ").title())

    plt.xlabel('Time [s]')
    plt.ylabel('CPU Usage [%]')
    plt.title('CPU Usage Over Time')
    plt.legend()
    plt.grid()
    plt.tight_layout()

    if args.save:
        plt.savefig(os.path.join(FIGDIR,"cpu.pdf"))
        print(f"Figure saved to {os.path.join(FIGDIR,'cpu.pdf')}")
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