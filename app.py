import subprocess

def execute(commands, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT):
    process = subprocess.Popen(commands, shell=shell, stdout=stdout, stderr=stderr)
    out, err = process.communicate()
    return (out if not err else err).split()

def inspect():
    devices = execute('''nvidia-smi | awk '$2=="Processes:" {p=1} p && $2 ~ /^[0-9]+$/ {print $2, $3}' ''')
    containers = execute('docker ps --format "{{ .Names }}"')
    processes = map(lambda c: list(map(int, execute("docker top {} | awk '{}'".format(c, '{p=1} p && $2 ~ /^[0-9]+$/ {print $2}')))), containers)
    gpus = devices[::2]
    gpuprocs = map(int, devices[1::2])
    for gpu, proc in zip(gpus, gpuprocs):
        belongs = []
        for container, containerproc in zip(containers, processes):
            if proc in containerproc:
                belongs = container


listOdd = list1[1::2] # Elements from list1 starting from 1 iterating by 2
listEven = list1[::2]

awk '$2=="Processes:" {p=1} p && $2 ~ /^[0-9]+$/ {print $2","$3}'

p = subprocess.Popen('ls', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for line in p.stdout.readlines():
    print line,
retval = p.wait()

@app.route('/')
def hello():
    return "Hello World!"

app = Flask(__name__)

if __name__ == '__main__':
    app.run()
