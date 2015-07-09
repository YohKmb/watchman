#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, Response #, request
import json
from lib import pinger
from threading import current_thread


app = Flask(__name__)
senders, receiver = None, None


@app.route("/history")
def history():
    hists = receiver.history
    return Response(json.dumps(
        [{"host":k, "history":list(v)} for k,v in hists.items() ]
    ))


@app.route("/main")
def main_page():
    return render_template("main.html")



@app.route("/test")
def test():
    # print "app : " + str(current_thread() )
    return render_template("test2.html")


if __name__ == "__main__":
    print "main : " + str(current_thread() )

    senders, receiver = pinger.generate_pingers(targets=["www.kernel.org", "web.mit.edu"])
    print "senders = " + str(senders)
    print "receiver = " + str(receiver)

    try:
        pinger.start_pingers(senders, receiver, is_fg=False)
        app.run(debug=False)
        # app.run(debug=True)
    finally:
        pinger.stop_pingers(senders, receiver)

