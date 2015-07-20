#! /usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Flask, render_template, Response
import json
import re

from lib import pinger

TARGETS_SAMPLE = ["www.kernel.org", "web.mit.edu", "www.google.com"]

app = Flask(__name__)
senders, receiver = None, None

scale_bar = 10
keyorder = [k for k in pinger.StatsPing(0,0,0,0)._asdict()]
print keyorder


@app.route("/history")
def history():
    stats = receiver.stats
    targets = {}
    for sender in senders:
        targets.update(sender.targets)

    hists = [{"host":k, "history":list(v), "stats":stats[k].as_record(), "fqdn":targets[k]} for k,v in receiver.history.items() ]

    return Response( json.dumps(hists) )

@app.route("/targets")
def targets():
    targets = {}
    for sender in senders:
        targets.update(sender.targets)

    return Response( json.dumps(targets) )

@app.route("/main")
def main_page():
    return render_template("main.html", scale_bar=scale_bar,
                           const_timeout=pinger.ResultPing.TIMEOUT,
                           const_keyorder=keyorder)

def _load_config(path_conf):
    conf = ""
    targets = {}

    try:
        with open(path_conf, "r") as rdf:
            conf = rdf.read()
        conf = re.sub(r'#.*', "", conf, re.MULTILINE)
        if len(conf):
                targets = json.loads(conf)
    except:
        pass

    return targets

def _get_targets_enabled(path_conf="./targets.config"):
    dict_target = _load_config(path_conf)

    if dict_target:
        return [targ for targ in dict_target.keys() if dict_target[targ]["enabled"]]
    else:
        print("No valid target was found. Failback and use example targets instead.")
        return TARGETS_SAMPLE


if __name__ == "__main__":
    targets = _get_targets_enabled()
    # senders, receiver = pinger.generate_pingers(targets=["localhost"])
    # senders, receiver = pinger.generate_pingers(targets=["localhost", "192.168.1.167"])
    # senders, receiver = pinger.generate_pingers(targets=["www.kernel.org", "web.mit.edu", "www.google.com"])
    senders, receiver = pinger.generate_pingers(targets=targets)

    try:
        pinger.start_pingers(senders, receiver, is_fg=False)
        app.run(debug=False)
    finally:
        pinger.stop_pingers(senders, receiver)
