watchman (beta)
====

Graphical ICMP Monitoring Tool

![demo](https://github.com/YohKmb/watchman/blob/master/.demo/watchman_demo_01.gif)

### Description

This repository offers you a browser-based ICMP monitoring tool "watchman" and CLI-based ping utility "lib/pinger.py".

The later is internally used in "watchman".

 - watchman : 

    As demonstrated in the animation above, you can dynamically monitor results and statistics of them of ICMP health-checking to multiple devices.
    Targets of ICMP can be editored from web-base gui. (You can directly modify json file, if you want.)

 - lib/pinger.py : 

    Pure-Python ICMP CLI utility tool. At this moment, this can work only on *nix platmfoms. (related to socket allocatin problem)


### Notes

At this moment, this package is in beta-version.
I'll support windows platforms and ping-springboards via ssh connections.

### Licence

MIT (https://github.com/YohKmb/watchman/blob/master/LICENSE)

### Author

Yoh Kamibayashi (https://github.com/YohKmb)

