#! /usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Flask, render_template, Response
import json

# from __future__ import division

from lib import pinger


app = Flask(__name__)
senders, receiver = None, None

scale_bar = 10


@app.route("/history")
def history():
    hists = receiver.history
    return Response(json.dumps(
        [{"host":k, "history":list(v)} for k,v in hists.items() ]
    ))

@app.route("/main")
def main_page():
    return render_template("main.html", scale_bar=scale_bar,
                           const_timeout=pinger.ResultPing.TIMEOUT)


if __name__ == "__main__":
    # senders, receiver = pinger.generate_pingers(targets=["localhost"])
    senders, receiver = pinger.generate_pingers(targets=["localhost", "192.168.1.161"])
    # senders, receiver = pinger.generate_pingers(targets=["www.kernel.org", "web.mit.edu"])

    try:
        pinger.start_pingers(senders, receiver, is_fg=False)
        app.run(debug=False)
    finally:
        pinger.stop_pingers(senders, receiver)
