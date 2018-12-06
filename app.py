import subprocess

from flask import Flask, render_template

def execute(commands, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT):
    process = subprocess.Popen(commands, shell=shell, stdout=stdout, stderr=stderr)
    out, err = process.communicate()
    return (out if not err else err).decode('utf-8').split()

def inspect():
    containers = execute('docker ps --format "{{ .Names }},{{ .Status }}"')
    processes = list(map(lambda c: list(map(int, execute("docker top {} | awk '{}'".format(c, '{p=1} p && $2 ~ /^[0-9]+$/ {print $2}')))), containers))
    devices = list(map(int, execute('''nvidia-smi | awk '$2=="Processes:" {p=1} p && $2 ~ /^[0-9]+$/ {print $2, $3}' ''')))

    for gpu, proc in zip(devices[::2], devices[1::2]):
        yield gpu, proc, *next(c.split(',') for c, ps in zip(containers, processes) if proc in ps)

app = Flask(__name__)

@app.route('/')
def blame():
    return render_template('blame.html', information=list(inspect()))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6006, debug=True)

