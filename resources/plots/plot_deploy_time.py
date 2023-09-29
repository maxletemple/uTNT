#!/opt/homebrew/bin/python3.11
import os
import re
import argparse
import statistics
import matplotlib.pyplot as plt
from collections import defaultdict

WORKDIR="../results/deploy"
FIGDIR="figures"

def convert_elapsed_time_to_float(time_str):
    parts = time_str.split(':')

    if len(parts) == 2:
        minutes, seconds = map(float, parts)
        total_seconds = minutes * 60 + seconds
    elif len(parts) == 3:
        hours, minutes, seconds = map(float, parts)
        total_seconds = hours * 3600 + minutes * 60 + seconds
    else:
        raise ValueError("Invalid time format")

    return total_seconds
        
def parse_perf_time(filename):
    f_regex = r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\):\s+([0-9]+:[0-9]+.[0-9]+)"
    with open(filename, "r") as f:
        content = f.read()
    
    matches = re.findall(f_regex, content)
    values = list()
    for match in matches:
        values.append(convert_elapsed_time_to_float(match))
    
    return values

def diff_time(t1, t2):
    time_difference_microseconds = t2 - t1

    # Convert the difference to more human-readable units
    microseconds_per_second = 1000000
    microseconds_per_minute = 60 * microseconds_per_second
    microseconds_per_hour = 60 * microseconds_per_minute

    remaining_microseconds = time_difference_microseconds % microseconds_per_hour
    remaining_microseconds %= microseconds_per_minute

    seconds = remaining_microseconds // microseconds_per_second
    remaining_microseconds %= microseconds_per_second
    
    return seconds+remaining_microseconds

def parse_output_time(filename):
    f_regex = r"(t[0-3]):\s([0-9]+)"
    with open(filename, "r") as f:
        content = f.read()
    
    matches = re.findall(f_regex, content)
    dict_time = defaultdict(list)
    
    for match in matches:
        dict_time[match[0]].append(match[1])
    
    values = list()
    for i, v in enumerate(dict_time["t2"]):
       values.append(diff_time(float(dict_time["t1"][i]),float(v)))
    
    return statistics.mean(values)

def iterate_files(workdir, data):
    for filename in sorted(os.listdir(workdir)):
        key = filename.split("_")[0]
        if "deploy" in filename:
            data[key].append(statistics.mean(parse_perf_time(os.path.join(workdir, filename))))
        elif "run_time" in filename: 
            data[key].append(statistics.mean(parse_perf_time(os.path.join(workdir, filename))))
        elif "vm_wget_time" in filename:
            data[key][-1] = data[key][-1] - statistics.mean(parse_perf_time(os.path.join(workdir, filename)))

def plot(args, data):
    plt.figure(figsize=(6, 3))  # Adjust the figure size if needed
    _, ax = plt.subplots()

    databox = defaultdict(list)
    for filename in sorted(os.listdir(args.workdir)):
        key = filename.split("_")[0]
        if "deploy" in filename:
            databox[key].append(parse_perf_time(os.path.join(args.workdir, filename)))
    categories = list(data.keys())
    values = list(data.values())

    # Transpose the values for proper stacking
    values_transposed = list(map(list, zip(*values)))

    # Plot each set of values as a stacked bar
    bottoms = [0] * len(categories)
    colors = ['#ff7f0e', '#1f77b4', '#2ca02c' , '#d62728']
    for i, value_set in enumerate(values_transposed):
        ax.bar(categories, value_set, bottom=bottoms, label=f'Value {i+1}', zorder=3, color=colors[i])
        #bottoms = [(x) for x in zip(bottoms, value_set)]
    plt.boxplot([databox["docker"][0], databox["utnt"][0], databox["vm"][0]], zorder=4, positions=[0,1,2], widths=0.6, showfliers=False, patch_artist=True, boxprops=dict(facecolor="#ff7f0e"), medianprops=dict(color="black"), whiskerprops=dict(color="black"), capprops=dict(color="black"))
    plt.grid(zorder=0)
    #plt.tight_layout()
    plt.xlabel('Categories')
    plt.ylabel('Time [s]')
    plt.legend(["Deploy time", "Execution time"])
    plt.title('Total execution time (deploy, create, run instance, destroy and cleanup)')

    if args.save:
        plt.savefig(os.path.join(FIGDIR,"total_execution_time.pdf"))
        print(f"Figure saved to {os.path.join(FIGDIR,'total_execution_time.pdf')}")
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
    print(data)
    plot(args, data)

    
if __name__ == "__main__":
    main()