#! /usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Flask, render_template, Response, request, jsonify #, redirect
import json, re, os, time

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

DEFAULT_CONFIGFILE = "./targets.config"

app = Flask(__name__)
senders, receiver = None, None
targets = None

path_conf = ""

scale_bar = 10
keyorder = [k for k in pinger.StatsPing(0,0,0,0)._asdict()]


@app.route("/history")
def history():
    stats = receiver.stats
    targets = {}
    for sender in senders:
        with sender.targets as s_target:
            targets.update(s_target)
        # targets.update(sender.targets)

    hists = [{"host":k, "history":list(v), "stats":stats[k].as_record(), "fqdn":targets[k]}
             for k,v in receiver.history.items() if k in targets ]

    return Response( json.dumps(hists) )

@app.route("/targets", methods=["GET", "POST"])
def targets():
    global targets, path_conf

    if (request.method == "GET"):
        return Response( json.dumps(targets) )

    elif (request.headers['Content-Type'] == 'application/json'):
        # print request.json
        targets = request.json
        _save_config(targets, path_conf)

        return jsonify(res='recept'), 200

    return jsonify(res='error'), 400

@app.route("/_restart")
def _restart():
    global senders, path_conf
    targets_list = _get_targets_enabled(path_conf)

    senders = pinger.restart_pingers(targets_list, senders)
    time.sleep(0.5)
    # print("restart was called")
    # return main_page()
    return jsonify(res='recept'), 200
    # return redirect("/main")

@app.route("/main")
def main_page():
    return render_template("main.html", scale_bar=scale_bar,
                           const_timeout=pinger.ResultPing.TIMEOUT,
                           const_keyorder=keyorder)

@app.route("/config")
def config_test():
    return render_template("config.html", targets=json.dumps(targets),
                           const_keyorder=["host", "description", "enabled", "ssh"])


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

def _save_config(dict_targets, path_conf):
    try:
        with open(path_conf, "w") as wdf:
            json.dump(dict_targets, wdf)
            print os.getcwd()
            print("Config was saved successfully.")

    except IOError as excpt:
        print excpt.message

def _get_targets_enabled(path_conf):
    global targets
    targets = _load_config(path_conf)

    if not targets:
        print("No valid target was found. Failback and use example targets instead.")
        targets = TARGETS_SAMPLE

    for targ in targets.keys():
        targets[targ]["host"] = targ

    return [targ for targ in targets.keys() if targets[targ]["enabled"]]

# def _setup():
#     global senders, receiver
#
#     path_conf = os.path.join(os.path.dirname(__file__), DEFAULT_CONFIGFILE)
#     targets_list = _get_targets_enabled(path_conf)
#
#     senders, receiver = pinger.generate_pingers(targets=targets_list)


if __name__ == "__main__":
    path_conf = os.path.join(os.path.dirname(__file__), DEFAULT_CONFIGFILE)
    targets_list = _get_targets_enabled(path_conf)
    # senders, receiver = pinger.generate_pingers(targets=["localhost"])
    # senders, receiver = pinger.generate_pingers(targets=["localhost", "192.168.1.167"])
    # senders, receiver = pinger.generate_pingers(targets=["www.kernel.org", "web.mit.edu", "www.google.com"])
    print targets_list
    senders, receiver = pinger.generate_pingers(targets_list=targets_list)

    try:
        pinger.start_pingers(senders, receiver, is_fg=False)
        app.run(debug=False)
    finally:
        pinger.stop_pingers(senders, receiver)
        print("Here, the {0} ends.".format(__file__))
