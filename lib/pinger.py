#! /usr/bin/env python


__author__ = "YohKmb <yoh134shonan@gmail.com"
__status__ = "development"
__version__ = "0.0.1"
__date__    = "July 2015"


import socket, struct, array
import sys, os, time, logging

from threading import Thread, Event
from collections import defaultdict, namedtuple
from functools import wraps
from contextlib import closing


# choose an apppropriate timer module depending on the platform
if sys.platform == "win32":
    default_timer = time.clock
else:
    default_timer = time.time


class ICMP():

    ICMP_ECHO_REQ = 0x08
    ICMP_ECHO_REP = 0x00

    PROTO_STRUCT_FMT = "!BBHHH"
    PROTO_CODE = socket.getprotobyname("icmp")

    NBYTES_TIME = struct.calcsize("d")

    def _checksum_wrapper(func):

        # if struct.pack("H",1) == "\x00\x01": # big endian
        if sys.byteorder == "big":

            @wraps(func)
            def _checksum_inner(cls, pkt):
                if len(pkt) % 2 == 1:
                    pkt += "\0"
                s = sum(array.array("H", pkt))
                s = (s >> 16) + (s & 0xffff)
                s += s >> 16
                s = ~s
                return s & 0xffff
        else:
            @wraps(func)
            def _checksum_inner(cls, pkt):
                if len(pkt) % 2 == 1:
                    pkt += "\0"
                s = sum(array.array("H", pkt))
                s = (s >> 16) + (s & 0xffff)
                s += s >> 16
                s = ~s
                return (((s>>8)&0xff)|s<<8) & 0xffff

        return _checksum_inner

    @classmethod
    @_checksum_wrapper
    def checksum(cls, pkt):
        pass


class ICMP_Request(ICMP):

    @classmethod
    def new_request(self, id, seq):

        # Temporary header whose checksum is set to 0
        chsum = 0

        # Tuple format := ("type", "code", "checksum", "id", "seq")
        req_header = struct.pack(ICMP_Request.PROTO_STRUCT_FMT,
                                 ICMP_Request.ICMP_ECHO_REQ, 0, chsum, id, seq)

        t_send = default_timer()
        # nbytes_t = struct.calcsize("d")

        data = (64 - ICMP.NBYTES_TIME) * "P"
        data = struct.pack("d", t_send) + data

        chsum = ICMP.checksum(req_header + data)
        req_header = struct.pack(ICMP.PROTO_STRUCT_FMT,
                                 ICMP.ICMP_ECHO_REQ, 0, chsum, id, seq)
        packet = req_header + data

        return packet


class ICMP_Reply(ICMP):

    @classmethod
    def decode_packet(self, packet, id_sent):

        header = packet[20:28]
        t_recv = default_timer()

        try:
            type, code, checksum, id_recv, seq = struct.unpack(ICMP.PROTO_STRUCT_FMT, header)
        except struct.error as excpt:
            logging.warning("invalid header was detected : {0}".format(str(header)))
            return None

        if type == ICMP.ICMP_ECHO_REP and id_recv == id_sent:
            t_send = struct.unpack("d", packet[28:28 + ICMP.NBYTES_TIME])[0]

            resp_time =  t_recv - t_send
            return (seq, resp_time)

        return None


# class ICMP_Echo(ICMP):
#
#     def __init__(self, id, seq):
#         super(ICMP_Echo, self).__init__(ICMP.ICMP_ECHO_REQ, 0, id, seq)
#
#     def _build_packet(self, id, seq):
#
#         chsum = 0
#         header = struct.pack(ICMP.PROTO_STRUCT_FMT, *tuple(self) )
#         # Temporary header whose checksum was set to 0
#
#         t_send = default_timer()
#         nbytes_t = struct.calcsize("d")
#         # nbytes_t = sys.getsizeof(t_send) / 8
#         data = (64 - nbytes_t) * "P"
#         data = struct.pack("d", t_send) + data
#
#         chsum = Pinger.checksum(header + data)
#         header = struct.pack(Pinger.PROTO_STRUCT_FMT,
#                                  Pinger.ICMP_ECHO_REQ, 0, chsum, self._id, seq)
#         packet = header + data
#
#         return packet

# req_header = struct.pack(Pinger.PROTO_STRUCT_FMT,
#                                  Pinger.ICMP_ECHO_REQ, 0, chsum, self._id, seq)
# header_decode = ICMP_Header_Tuple( *(struct.unpack(Pinger.PROTO_STRUCT_FMT, header)) )

# class ICMP_Echo(ICMP_Header_Tuple):
#
#     def __repr__(self):
#         return self._asdict()


class Pinger(Thread):

    # ICMP_ECHO_REQ = 0x08
    # ICMP_ECHO_REP = 0x00

    MAX_TARGET = 5
    INTERVAL_PING = 1.0
    LEN_RECV = 1024

    PROTO_STRUCT_FMT = "!BBHHH"
    # PROTO_CODE = socket.getprotobyname("icmp")
    # ICMP_Header = namedtuple("ICMP_Header", ("type", "code", "checksum", "id", "seq"))

    def __init__(self, targets=[], timeout=3.0, is_receiver=False):

        super(Pinger, self).__init__()

        self._id = os.getpid() & 0xFFFF
        self._is_receiver = is_receiver
        self._targets = targets
        self._timeout = timeout
        self._seqs = defaultdict(lambda: 1)

        self.daemon = True
        self._ev = Event()

    def run(self):

        try:
            with closing(socket.socket(family=socket.AF_INET, type=socket.SOCK_RAW,
                                         proto=ICMP.PROTO_CODE) ) as sock:
                # print sock
                if not self._is_receiver:
                    self._work_on_myduty = self._send

                else:
                    self._work_on_myduty = self._recv

                while True:
                    res = self._work_on_myduty(sock)
                    print res
                    # print res, str(self._work_on_myduty)

                    if self._ev.is_set():
                        break

        except socket.error as excpt:
            logging.error(excpt.__class__)
            sys.exit(1)

    def end(self):
        self._ev.set()

    @property
    def targets(self):
        return self._targets

    @targets.setter
    def targets(self, targets):

        resolved = []
        for target in targets:
            try:
                addr_dst = socket.gethostbyname(target)
                resolved.append(addr_dst)

            except socket.gaierror as excpt:
                logging.warning("{0} -> {1} is ignored".format(excpt.message, target))
                targets.remove(target)

        self._targets = dict( zip(targets, resolved) )

    def _send(self, sock):
        # print str(self._targets)
        results = []

        for target in self._targets.values():
            print target
            res = self._send_one(sock, target)
            results.append(res)

        time.sleep(1.0)
        return results

    def _recv(self, sock):

        try:
            packet, addr_port = sock.recvfrom(Pinger.LEN_RECV)
        except socket.timeout as excpt:
            logging.info("receive timeout occurred")
            return None

        seq, resp_time = ICMP_Reply.decode_packet(packet, self._id)
        return resp_time

        # header = packet[20:28]
        # t_recv = default_timer()
        #
        # try:
        #     # header_decode = struct.unpack(ICMP.PROTO_STRUCT_FMT, header)
        #     # header_decode = ICMP_Header( *(struct.unpack(Pinger.PROTO_STRUCT_FMT, header)) )
        #     type, code, checksum, id, seq = struct.unpack(Pinger.PROTO_STRUCT_FMT, header)
        # except struct.error as excpt:
        #     logging.warning("invalid header was detected : {0}".format(str(header)))
        #     return None
        #
        # if type == ICMP.ICMP_ECHO_REP and id == self._id:
        #     nbytes_time = struct.calcsize("d")
        #     t_send = struct.unpack("d", packet[28:28 + nbytes_time])[0]
        #
        #     return t_recv - t_send

    def _send_one(self, sock, addr_dst):
        # try:
        #     addr_dst = socket.gethostbyname(name_dst)
        #
        # except socket.gaierror as excpt:
        #     logging.warning("{0} -> {1} is ignored".format(excpt.message, name_dst))
        #     self._targets.remove(name_dst)
        #     return
        seq = self._seqs[addr_dst]
        packet = ICMP_Request.new_request(self._id, seq)
        # packet = self._build_packet(seq)
        self._seqs[addr_dst] += 1
        # print packet

        try:
            len_send = sock.sendto(packet, (addr_dst, 0))
            # print "sent " + str(len_send) + " packets"

        except socket.error as excpt:
            logging.error("failed to sending to {0}".format(addr_dst))
            raise excpt

        # assert len_send is not None, "send None"
        # print "len_send = " + str(len_send)
        return len_send

    # def _recv_one(self):
    #     pass

    def _checksum_wrapper(func):

        # if struct.pack("H",1) == "\x00\x01": # big endian
        if sys.byteorder == "big":

            @wraps(func)
            def _checksum_inner(cls, pkt):
                if len(pkt) % 2 == 1:
                    pkt += "\0"
                s = sum(array.array("H", pkt))
                s = (s >> 16) + (s & 0xffff)
                s += s >> 16
                s = ~s
                return s & 0xffff
        else:
            @wraps(func)
            def _checksum_inner(cls, pkt):
                if len(pkt) % 2 == 1:
                    pkt += "\0"
                s = sum(array.array("H", pkt))
                s = (s >> 16) + (s & 0xffff)
                s += s >> 16
                s = ~s
                return (((s>>8)&0xff)|s<<8) & 0xffff

        return _checksum_inner

    @classmethod
    @_checksum_wrapper
    def checksum(cls, pkt):
        pass

    def _build_packet(self, seq):

        chsum = 0
        req_header = struct.pack(Pinger.PROTO_STRUCT_FMT,
                                 Pinger.ICMP_ECHO_REQ, 0, chsum, self._id, seq)
        # Temporary header whose checksum was set to 0

        t_send = default_timer()
        nbytes_t = struct.calcsize("d")
        # nbytes_t = sys.getsizeof(t_send) / 8
        data = (64 - nbytes_t) * "P"
        data = struct.pack("d", t_send) + data

        chsum = Pinger.checksum(req_header + data)
        req_header = struct.pack(Pinger.PROTO_STRUCT_FMT,
                                 Pinger.ICMP_ECHO_REQ, 0, chsum, self._id, seq)
        packet = req_header + data

        return packet


def main():
    s1 = Pinger()
    r1 = Pinger(is_receiver=True)
    s1.targets = ["www.google.com", "www.kernel.org"]

    try:
        s1.start()
        r1.start()

        while True:
            raw_input()

    except KeyboardInterrupt as excpt:
        # print(excpt)

        logging.info("Keyboard Interrupt occur. Program will exit.")

        s1.end()
        r1.end()

        s1.join()
        r1.join()

        sys.exit(0)

    logging.info("main program exits")


if __name__ == "__main__":
    main()
