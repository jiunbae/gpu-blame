import subprocess
from functools import partial
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, redirect, url_for

class Inspect:
    cache = list()
    last = datetime.now()

    columns = "#,PID,Container,Status,CPU,Memory,GPU,Memory".split(',')

    @staticmethod
    def __exe(commands, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT):
        process = subprocess.Popen(commands, shell=shell, stdout=stdout, stderr=stderr)
        out, err = process.communicate()
        return (out if not err else err).decode('utf-8')

    @staticmethod
    def __inspect():
        containers = list(map(partial(str.split, sep=','), Inspect.__exe('docker ps --format "{{ .Names }},{{ .Status }}"').splitlines()))
        processes = list(map(lambda c: Inspect.__exe("docker top {} | awk '{}'".format(c[0], '{p=1} p && $2 ~ /^[0-9]+$/ {print $2}')).split(), containers))
        stats = {line.split()[0]: line.split()[1:] for line in Inspect.__exe("docker stats --no-stream | awk 'NR-1 > 0 { print $2, $3, $4 }'").splitlines()}
        devices = Inspect.__exe('''nvidia-smi | awk '$2=="Processes:" {p=1} p && $2 ~ /^[0-9]+$/ {print $2, $3}' ''').split()
        utils = list(map(partial(str.split, sep=','), Inspect.__exe('''nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader''').splitlines()))
        
        for gpu, proc in zip(map(int, devices[::2]), devices[1::2]):
            container, status = next(c for c, ps in zip(containers, processes) if proc in ps)
            yield (gpu, [proc, container, status, *stats[container], *utils[gpu]])

    @staticmethod
    def update():
        Inspect.cache = list(Inspect.__inspect())
        Inspect.last = datetime.now()

    @staticmethod
    def info():
        return Inspect.cache, Inspect.last

app = Flask(__name__)

scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(Inspect.update, 'interval', minutes=1)
scheduler.start()

@app.route('/refresh')
def refresh():
    Inspect.update()
    return redirect(url_for('blame'))

@app.route('/')
def blame():
    info, stamp = Inspect.info()
    return render_template('blame.html', columns=Inspect.columns, information=info, stamp=stamp.strftime("%Y-%m-%d %H:%M"))

if __name__ == '__main__':
    Inspect.update()
    app.run(host='0.0.0.0', port=6006, debug=True)
