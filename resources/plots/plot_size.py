#!/opt/homebrew/bin/python3.11
import os
import argparse
import matplotlib.pyplot as plt
import csv

FILENAME="../results/size_all.csv"
FIGDIR="figures"

def parse_csv(filename):
    labels = []
    values = []
    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')
        for i, row in enumerate(csvreader):
            if i == 0:
                continue
            labels.append(row[0])
            values.append(float(row[1]))
    return (labels, values)

def plot(args, data):
    labels, values = data

    plt.figure(figsize=(6, 3))
    barlist=plt.bar(labels, values)
    colors = ['#1f77b4','#ff7f0e',  '#2ca02c','#d62728']
    for i,bar in enumerate(barlist):
        bar.set_color(colors[i])

    plt.yscale('log')
    plt.xlabel('Categories')
    plt.ylabel('File Size [MB]')
    plt.title('Filesize of images')
    plt.xticks(rotation=45)
    plt.tight_layout()
    if args.save:
        plt.savefig(os.path.join(FIGDIR,"filesize.pdf"))
        print(f"Figure saved to {os.path.join(FIGDIR,'filesize.pdf')}")
    if args.show:
        plt.show()

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", type=str, default=FILENAME, help="Path to the csv file")
    parser.add_argument("--show", required=False, default=False, action="store_true", help="Display plot")
    parser.add_argument("--save", required=False, default=True, action="store_true", help="Save plot to pdf")
    args = parser.parse_args()
    
    data = parse_csv(args.filename)
    plot(args, data)

if __name__ == "__main__":
    main()