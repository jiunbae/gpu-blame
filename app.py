import subprocess

from flask import Flask, render_template

def execute(commands, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT):
    process = subprocess.Popen(commands, shell=shell, stdout=stdout, stderr=stderr)
    out, err = process.communicate()
    return (out if not err else err).decode('utf-8').split()

def inspect():
    devices = list(map(int, execute('''nvidia-smi | awk '$2=="Processes:" {p=1} p && $2 ~ /^[0-9]+$/ {print $2, $3}' ''')))
    containers = execute('docker ps --format "{{ .Names }}"')
    processes = list(map(lambda c: list(map(int, execute("docker top {} | awk '{}'".format(c, '{p=1} p && $2 ~ /^[0-9]+$/ {print $2}')))), containers))
    gpus, gprocs = devices[::2], devices[1::2]
    
    for gpu, proc in zip(gpus, gprocs):
        belongs = next(c for c, ps in zip(containers, processes) if proc in ps)
        yield gpu, proc, belongs

app = Flask(__name__)

@app.route('/')
def blame():
    gpus = list(inspect())
    print (gpus)
    return render_template('blame.html', gpus=gpus)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6006, debug=True)

