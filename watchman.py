#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, Response #, request
import json
from lib import pinger


app = Flask(__name__)
senders, receiver = None, None


@app.route("/history")
def history():
    return Response(json.dumps(receiver.history.keys() ))


@app.route("/main")
def main_page():
    return render_template("queue.html")



@app.route("/test")
def test():
    # print "app : " + str(current_thread() )
    return render_template("test2.html")


if __name__ == "__main__":
    # print "main : " + str(current_thread() )
    senders, receiver = pinger.generate_pingers(targets=["www.kernel.org", "web.mit.edu"])
    pinger.start_pingers(senders, receiver, is_fg=False)
    app.run(debug=True)


