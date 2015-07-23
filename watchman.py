#! /usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Flask, render_template, Response, request
import json
import re

from lib import pinger

TARGETS_SAMPLE = {
    "www.kernel.org": {
        "description": "Kernel.org",
        "enabled": True,
        "ssh": False
    },
    "web.mit.edu": {
        "description": "MIT",
        "enabled": True,
        "ssh": False
    },
    "www.google.com": {
        "description": "Google",
        "enabled": True,
        "ssh": False
    }
}

app = Flask(__name__)
senders, receiver = None, None
targets = None

scale_bar = 10
keyorder = [k for k in pinger.StatsPing(0,0,0,0)._asdict()]


@app.route("/history")
def history():
    stats = receiver.stats
    targets = {}
    for sender in senders:
        targets.update(sender.targets)

    hists = [{"host":k, "history":list(v), "stats":stats[k].as_record(), "fqdn":targets[k]} for k,v in receiver.history.items() ]

    return Response( json.dumps(hists) )

@app.route("/targets", methods=["GET", "POST"])
def targets():
    if (request.method == "GET"):
        return Response( json.dumps(targets) )
    else:
        pass

@app.route("/main")
def main_page():
    return render_template("main.html", scale_bar=scale_bar,
                           const_timeout=pinger.ResultPing.TIMEOUT,
                           const_keyorder=keyorder)

@app.route("/config_test")
def config_test():
    return render_template("config_test.html", targets=json.dumps(targets),
                           const_keyorder=["host", "description", "enabled", "ssh"])
                           # const_keyorder=["host", "description", "enabled", "ssh", "delete"])


def _load_config(path_conf):
    conf = ""
    dict_targets = {}
    try:
        with open(path_conf, "r") as rdf:
            conf = rdf.read()
        conf = re.sub(r'#.*', "", conf, re.MULTILINE)
        if len(conf):
                dict_targets = json.loads(conf)
    except:
        pass

    return dict_targets

def _get_targets_enabled(path_conf="./targets.config"):
    global targets
    targets = _load_config(path_conf)

    if not targets:
        print("No valid target was found. Failback and use example targets instead.")
        targets = TARGETS_SAMPLE

    for targ in targets.keys():
        targets[targ]["host"] = targ

    return [targ for targ in targets.keys() if targets[targ]["enabled"]]

if __name__ == "__main__":
    targets_list = _get_targets_enabled()
    # senders, receiver = pinger.generate_pingers(targets=["localhost"])
    # senders, receiver = pinger.generate_pingers(targets=["localhost", "192.168.1.167"])
    # senders, receiver = pinger.generate_pingers(targets=["www.kernel.org", "web.mit.edu", "www.google.com"])
    senders, receiver = pinger.generate_pingers(targets=targets_list)

    try:
        pinger.start_pingers(senders, receiver, is_fg=False)
        app.run(debug=False)
    finally:
        pinger.stop_pingers(senders, receiver)
