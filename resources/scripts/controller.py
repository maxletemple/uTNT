import argparse
import time
import threading
import paramiko
import os

class Node:
    def __init__(self, ip, username, key):
        self.ip = ip
        self.username = username
        self.key = key
        self.inUse = False

class Result:
    def __init__(self, start_time, send_time, end_time, res):
        self.start_time = start_time
        self.send_time = send_time
        self.end_time = end_time
        self.res = res
    
    def save_result(self):
        if not os.path.exists("../results/deploy_controller/utnt"):
            os.makedirs("../results/deploy_controller/utnt")
        if not os.path.exists("../results/deploy_controller/vm"):
            os.makedirs("../results/deploy_controller/vm")
        if not os.path.exists("../results/deploy_controller/docker"):
            os.makedirs("../results/deploy_controller/docker")
            
        match args.type:
            case "utnt":
                path = f"../results/deploy_controller/utnt/{args.filename}.txt"
            case "vm":
                path = f"../results/deploy_controller/vm/{args.filename}.txt"
            case "docker":
                path = f"../results/deploy_controller/docker/{args.filename}.txt"


        with open(path, "a") as f:
            f.write(f"{self.start_time},{self.send_time},{self.end_time},\n{self.res}\n")
    
    def save_result_csv(self):

        if not os.path.exists("../results/deploy_controller/utnt"):
            os.makedirs("../results/deploy_controller/utnt")
        if not os.path.exists("../results/deploy_controller/vm"):
            os.makedirs("../results/deploy_controller/vm")
        if not os.path.exists("../results/deploy_controller/docker"):
            os.makedirs("../results/deploy_controller/docker")
         
        match args.type:
            case "utnt":
                path = f"../results/deploy_controller/utnt/{args.filename}.csv"
            case "vm": 
                path = f"../results/deploy_controller/vm/{args.filename}.csv"
            case "docker":
                path = f"../results/deploy_controller/docker/{args.filename}.csv"
        with open(path, "a") as f:
            if os.stat(path).st_size == 0:
                f.write("start_time,send_time,start_booting, start_scamper, end_scamper,end_time\n")
            
            index_start = self.res.find("t0: ")
            index_end = self.res.find("\n", index_start)    
            start_booting = float(self.res[index_start+3:index_end])
            index_start = self.res.find("t1: ")
            index_end = self.res.find("\n", index_start)
            start_scamper = float(self.res[index_start+3:index_end])
            index_start = self.res.find("t2: ")
            index_end = self.res.find("\n", index_start)
            end_scamper = float(self.res[index_start+3:index_end])

            f.write("{:.3f},{:.3f},{:.3f},{:.3f},{:.3f},{:.3f}\n".format(self.start_time, self.send_time, start_booting/1000, start_scamper/1000000, end_scamper/1000000, self.end_time))


def get_available_node(nodes):
    if args.force:
        for node in nodes:
            if not node.inUse and waiting_threads[0] == threading.current_thread():
                return node
        return None
    else:
        for node in nodes:
            if not node.inUse:
                return node
        return None


def start_thread():
    if args.force:
        waiting_threads.append(threading.current_thread())
        node = None
        while node is None:
            node = get_available_node(nodes)
            time.sleep(.1)
        waiting_threads.remove(threading.current_thread())
    else:
        node = get_available_node(nodes)
        if node is None:
            print("No available node")
            return
    print(f"Starting thread on node {node.ip}")
    node.inUse = True
    match args.type:
        case "utnt":
            send_utnt(node)
        case "vm":
            send_vm(node)
        case "docker":
            send_docker(node)
    node.inUse = False
    global completed_events
    completed_events += 1

def send_file(client, local_path, remote_path):
    sftp = client.open_sftp()
    sftp.put(local_path, remote_path)
    sftp.close()

def execute_command(client, command):
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode("utf-8")
    return output

def load_client(node):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(node.ip, username=node.username, key_filename=node.key)
    return client

def send_utnt(node):
    client = load_client(node)
    tstart = time.time()
    channel = client.get_transport().open_session()
    send_file(client, "script_deploy_controller/deploy_utnt.sh", f"/home/{node.username}/deploy_utnt.sh")
    tsend_file = time.time()
    channel.exec_command("sh ~/deploy_utnt.sh")
    channel.recv_exit_status()
    texec = time.time()
    res = channel.recv(4096).decode("utf-8")
    result = Result(tstart, tsend_file, texec, res)
    result.save_result()
    result.save_result_csv()

def send_vm(node):
    client = load_client(node)
    tstart = time.time()
    channel = client.get_transport().open_session()
    send_file(client, f"script_deploy_controller/deploy_vm.sh", f"/home/{node.username}/deploy_vm.sh")
    send_file(client, f"../vagrant/Vagrantfile", f"/home/{node.username}/Vagrantfile")
    tsend_file = time.time()
    channel.exec_command(f"sh /home/{node.username}/deploy_vm.sh")
    channel.recv_exit_status()
    res = channel.recv(65536).decode("utf-8")
    texec = time.time()
    result = Result(tstart, tsend_file, texec, res)
    result.save_result()
    result.save_result_csv()

def send_docker(node):
    client = load_client(node)
    tstart = time.time()
    channel = client.get_transport().open_session()
    send_file(client, "script_deploy_controller/deploy_docker.sh", f"/home/{node.username}/deploy_docker.sh")
    tsend_file = time.time()
    channel.exec_command(f"sh /home/{node.username}/deploy_docker.sh")
    channel.recv_exit_status()
    resstr = channel.recv(65536).decode("utf-8")
    texec = time.time()
    result = Result(tstart, tsend_file, texec, resstr)
    result.save_result()
    result.save_result_csv()


parser = argparse.ArgumentParser()
parser.add_argument("type", type=str, choices=["utnt", "vm", "docker"])
parser.add_argument("filename", type=str)
parser.add_argument("--force", required=False, default=False, action="store_true")

with open("nodes.csv", "r") as f:
    contenu = f.read()
    lines = contenu.split("\n")
    nodes = []
    for line in lines:
        if line != "":
            ip, username, key = line.split(",")
            nodes.append(Node(ip, username, key))


args = parser.parse_args()

with open("list_events.txt", "r") as f:
    contenu = f.read()
    nb_str = contenu.split(",")
    events = [int(nb.strip()) for nb in nb_str]

start_time = time.time()
threads = []
waiting_threads = []
completed_events = 0
while True:
    current_time = time.time()
    elapsed_time = int(current_time - start_time)
    print(f"Elapsed time: {elapsed_time}")
    indexes = [i for i in range(len(events)) if events[i] == elapsed_time]
    for index in indexes:
        threads.append(threading.Thread(target=start_thread))
        threads[-1].start()
    if elapsed_time > max(events):
        break
    time.sleep(1)

print("Waiting for nodes to finish...")

for thread in threads:
    thread.join()

print(f"Completed events: {completed_events}/{len(events)}")