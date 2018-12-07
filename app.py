import subprocess
from functools import partial
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, redirect, url_for

class Inspect:

    @staticmethod
    def __exe(commands, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT):
        process = subprocess.Popen(commands, shell=shell, stdout=stdout, stderr=stderr)
        out, err = process.communicate()
        return (out if not err else err).decode('utf-8')

    @staticmethod
    def __inspect():
        containers = list(map(partial(str.split, sep=','), Inspect.__exe('docker ps --format "{{ .Names }},{{ .Status }}"').splitlines()))
        processes = list(map(lambda c: Inspect.__exe("docker top {} | awk '{}'".format(c[0], '{p=1} p && $2 ~ /^[0-9]+$/ {print $2}')).split(), containers))
        devices = Inspect.__exe('''nvidia-smi | awk '$2=="Processes:" {p=1} p && $2 ~ /^[0-9]+$/ {print $2, $3, $6}' ''').split()

        for gpu, proc, mem in zip(devices[::3], devices[1::3], devices[2::3]):
            yield (gpu, proc, mem, *next(c for c, ps in zip(containers, processes) if proc in ps))

    @staticmethod
    def update():
        Inspect.cache = list(Inspect.__inspect())
        Inspect.last = datetime.now()

    @property
    @staticmethod
    def info():
        return Inspect.cache, Inspect.last

app = Flask(__name__)

scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(Inspect.update, 'interval', minutes=10)
scheduler.start()

@app.route('/refresh'):
def refresh():
    Inspect.update()
    return redirect(url_for('/'))

@app.route('/')
def blame():
    info, stamp = Inspect.info
    return render_template('blame.html', information=info, stamp=stamp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6006, debug=True)
