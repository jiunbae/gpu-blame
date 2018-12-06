import subprocess
from functools import partial

from flask import Flask, render_template

def execute(commands, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT):
    process = subprocess.Popen(commands, shell=shell, stdout=stdout, stderr=stderr)
    out, err = process.communicate()
    return (out if not err else err).decode('utf-8')

def inspect():
    containers = list(map(partial(str.split, sep=','), execute('docker ps --format "{{ .Names }},{{ .Status }}"').splitlines()))
    processes = list(map(lambda c: execute("docker top {} | awk '{}'".format(c[0], '{p=1} p && $2 ~ /^[0-9]+$/ {print $2}')).split(), containers))
    devices = execute('''nvidia-smi | awk '$2=="Processes:" {p=1} p && $2 ~ /^[0-9]+$/ {print $2, $3, $6}' ''').split()

    for gpu, proc, mem in zip(devices[::3], devices[1::3], devices[2::3]):
        yield (gpu, proc, mem, *next(c for c, ps in zip(containers, processes) if proc in ps))

app = Flask(__name__)

@app.route('/')
def blame():
    return render_template('blame.html', information=list(inspect()))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6006, debug=True)

