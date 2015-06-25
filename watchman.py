#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, Response
import json
# from functools import wraps
from threading import Thread
from Queue import Queue
from random import randint
from time import sleep

q_thrds = None
# q_disp = []
q_disp = {}


class Queuinger(Thread):
    def __init__(self):
        super(Queuinger, self).__init__()

        self.daemon = True
        self.queue = Queue()

    def run(self):
        while True:
            self.queue.put(randint(0, 9))
            sleep(randint(1, 3))

    def get_added(self):
        added = []
        while not self.queue.empty():
            added.append(self.queue.get())

        return added


app = Flask(__name__)


@app.route("/queues")
def queues():
    # print str(q_disp)
    map_added = map(lambda (idx, thrd): (idx, thrd.get_added()), q_thrds.items())
    for idx, added in map_added:
        # q_disp.append({"name":idx, "results":added})
        q_disp[idx]["results"] = (q_disp[idx]["results"] + added)[-10:]

    return Response(json.dumps(q_disp.values()))
    # return Response(json.dumps([{k:v} for (k,v) in q_disp.items()]) )


@app.route("/main")
def main_page():
    # map_added = map(lambda (idx, thrd): (idx, thrd.get_added() ), q_thrds.items() )
    # for idx, added in map_added:
    #     q_disp[idx] = (q_disp[idx] + added)[-10:]
    return render_template("queue.html")

    # return "{0}".format(
    #     map(lambda (idx, thrd): (idx, thrd.get_added() ),
    #         q_thrds.items()
    #     )
    # )


@app.route("/test")
def test():
    return render_template("test2.html")


# @app.route("/user")
# @app.route("/user/<name>")
# def user(name=None):
#     # return {"user" : name}
#     return render_template("content_user.html", user=name)

# @app.route("/user")
# def user():
#     return render_template("content_user.html", user=None)


# @app.route("/queue")
# def queue():
#     pass
#
#
# def rotate_queue():
#     pass

def start_queuing():
    thrds = {}

    for i in xrange(3):
        thrd = Queuinger()
        thrds[i] = thrd
        q_disp[i] = {"name": i, "results": []}
        thrd.start()

    return thrds


if __name__ == "__main__":
    q_thrds = start_queuing()
    app.run(debug=True)
