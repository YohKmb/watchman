Watchman (beta)
====

Graphical ICMP Monitoring Tool

![demo](https://github.com/YohKmb/watchman/blob/master/.demo/watchman_demo_01.gif)

### Description

This repository offers you a browser-based ICMP monitoring tool "watchman" and CLI-based ping utility "lib/pinger.py".

The later is internally used in "watchman".

 - watchman : 

    As demonstrated in the animation above, you can dynamically monitor results and statistics of them of ICMP health-checking to multiple devices.
    Targets of ICMP can be editored from web-base gui. (You can directly modify json file, if you want.)
    
    As you guess, this tool was named after a certain great graphic novel.
    
    [Usage]
    
        1) Execute "watchman" script with an administrator privilege.
        2) Open your favarite web-browser. (Please not so obsolete version...)
        3) Access to http://localhost:5000/main or http://localhost:5000/ .
        4) Play like the demo animation above.
      
 - lib/pinger.py : 

    Pure-Python ICMP CLI utility tool. At this moment, this can work only on *nix platmfoms. (related to socket allocatin problem)


### Notes

 - Administrator Privilege

    You have to execute scripts in this repository with an administor privilege.
    It's required to open sockets.

 - Future Support for Windows Platforms

    At this moment, this package is in beta-version. I'll support windows platforms and ping-springboards via ssh connections.
    It's also planned to support IPv6.


### Requirement

 - Flask >= 0.10.1


### Licence

MIT (https://github.com/YohKmb/watchman/blob/master/LICENSE)

### Author

Yoh Kamibayashi (https://github.com/YohKmb)

