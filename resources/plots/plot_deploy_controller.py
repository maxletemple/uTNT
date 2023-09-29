import os
import argparse
import matplotlib.pyplot as plt
from collections import defaultdict

WORKDIR="../results/deploy_controller"
FIGDIR="figures"

def parse_file(filename):
    data_csv = defaultdict(list)
    linecount = 0
    with open(filename, "r") as f:
        content = f.read()
        lines = content.split("\n")
        lines.pop(0)
        for line in lines:
            if line != "":
                linecount += 1
                values = line.split(",")
                data_csv["start_time"].append(float(values[0]))
                data_csv["send_time"].append(float(values[1]))
                data_csv["start_booting"].append(float(values[2]))
                data_csv["start_scamper"].append(float(values[3]))
                data_csv["end_scamper"].append(float(values[4]))
                data_csv["end_time"].append(float(values[5]))
    return linecount, data_csv

def plot_deploy_amount():
    dataset = defaultdict(list)
    for filename in os.listdir(f"{WORKDIR}/utnt"):
        if filename.endswith(".csv"):
            lines, data = parse_file(os.path.join(f"{WORKDIR}/utnt",filename))
            dataset["utnt"].append(lines)
    for filename in os.listdir(f"{WORKDIR}/docker"):
        if filename.endswith(".csv"):
            lines, data = parse_file(os.path.join(f"{WORKDIR}/docker",filename))
            dataset["docker"].append(lines)
    for filename in os.listdir(f"{WORKDIR}/vm"):
        if filename.endswith(".csv"):
            lines, data = parse_file(os.path.join(f"{WORKDIR}/vm",filename))
            dataset["vm"].append(lines)

    plt.figure(figsize=(6, 3))
    fig, ax = plt.subplots()

    categories = ["utnt", "docker", "vm"]
    plt.boxplot([dataset["utnt"], dataset["docker"], dataset["vm"]], zorder=2, positions=[0,1,2], widths=0.6, showfliers=False, patch_artist=True, boxprops=dict(facecolor="#ff7f0e"), medianprops=dict(color="black"), whiskerprops=dict(color="black"), capprops=dict(color="black"))
    plt.bar(categories, [sum(dataset["utnt"])/len(dataset["utnt"]), sum(dataset["docker"])/len(dataset["docker"]), sum(dataset["vm"])/len(dataset["vm"])], zorder=1, color=["#ff7f0e", "#1f77b4", "#2ca02c"])
    
    plt.grid(zorder=0)
    plt.xlabel("Category")
    plt.ylabel("Number of successful runs")
    plt.title("Successful runs of controller (1 run per second)")


    plt.savefig(os.path.join(FIGDIR, "deploy_controller.pdf"))

def plot_deploy_time():
    dataset = defaultdict(list)
    for filename in os.listdir(f"{WORKDIR}/utnt"):
        if filename.endswith(".csv"):
            lines, data = parse_file(os.path.join(f"{WORKDIR}/utnt",filename))
            dataset["utnt"].append(data)
    for filename in os.listdir(f"{WORKDIR}/docker"):
        if filename.endswith(".csv"):
            lines, data = parse_file(os.path.join(f"{WORKDIR}/docker",filename))
            dataset["docker"].append(data)
    for filename in os.listdir(f"{WORKDIR}/vm"):
        if filename.endswith(".csv"):
            lines, data = parse_file(os.path.join(f"{WORKDIR}/vm",filename))
            dataset["vm"].append(data)

    plt.figure(figsize=(6, 3))
    fig, ax = plt.subplots()

    categories = ["utnt", "docker", "vm"]
    mean_utnt_time = 0
    mean_docker_time = 0
    mean_vm_time = 0
    means_utnt, means_docker, means_vm = [], [], []
    for i in range(len(dataset["utnt"])):
        mean_utnt_time += (sum(dataset["utnt"][i]["end_time"]) - sum(dataset["utnt"][i]["start_time"])) / len(dataset["utnt"][i]["end_time"])
        means_utnt.append((sum(dataset["utnt"][i]["end_time"]) - sum(dataset["utnt"][i]["start_time"])) / len(dataset["utnt"][i]["end_time"]))
    mean_utnt_time /= len(dataset["utnt"])

    for i in range(len(dataset["docker"])):
        mean_docker_time += (sum(dataset["docker"][i]["end_time"]) - sum(dataset["docker"][i]["start_time"])) / len(dataset["docker"][i]["end_time"])
        means_docker.append((sum(dataset["docker"][i]["end_time"]) - sum(dataset["docker"][i]["start_time"])) / len(dataset["docker"][i]["end_time"]))
    mean_docker_time /= len(dataset["docker"])

    for i in range(len(dataset["vm"])):
        mean_vm_time += (sum(dataset["vm"][i]["end_time"]) - sum(dataset["vm"][i]["start_time"])) / len(dataset["vm"][i]["end_time"])
        means_vm.append((sum(dataset["vm"][i]["end_time"]) - sum(dataset["vm"][i]["start_time"])) / len(dataset["vm"][i]["end_time"]))
    mean_vm_time /= len(dataset["vm"])

    plt.grid(zorder=0)
    plt.xlabel("Category")
    plt.ylabel("Time [s]")
    plt.yscale("log")
    plt.title("Average execution time of controller (1 run per second)")

    plt.bar(categories, [mean_utnt_time, mean_docker_time, mean_vm_time], zorder=1, color=["#ff7f0e", "#1f77b4", "#2ca02c"])
    plt.boxplot([means_utnt, means_docker, means_vm], zorder=2, positions=[0,1,2], widths=0.6, showfliers=False, patch_artist=True, boxprops=dict(facecolor="#ff7f0e"), medianprops=dict(color="black"), whiskerprops=dict(color="black"), capprops=dict(color="black"))
    plt.savefig(os.path.join(FIGDIR, "deploy_controller_time.pdf"))


def main():

    plot_deploy_amount()
    plot_deploy_time()
    
    

if __name__ == "__main__":
    main()