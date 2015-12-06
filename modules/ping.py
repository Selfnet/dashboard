import logging
import subprocess # ever tried urllib in python3 on debian stable?

from .base.sources import TimedSource



class Ping(TimedSource):

    def pingcall(self, host, count=1, timeout=1, protocol=4):
        if protocol == 4:
            cmd = "ping"
        else:
            cmd = "ping6"
        args = [
            cmd,
            "-c", "1",
            "-i", "0.2",
            "-c", str(count),
            "-W", str(timeout),
            str(host)
        ]
        process = subprocess.Popen(args, stdout=subprocess.PIPE)
        out, err = process.communicate()
        return out

    def poll(self):
        host = self.get_config("host")
        count = self.get_config("count", 1)
        timeout = self.get_config("timeout", 1)
        protocol = self.get_config("protocol", 4)
        if protocol == 6 or str(protocol)[-1] == "6":
            protocol = 6
        else:
            protocol = 4
        try:
            out = self.pingcall(host, count, timeout, protocol)
            lastline = out.strip().split(b"\n")[-1]
            if lastline.startswith(b"rtt min/avg/max/mdev = "):
                rtt = float(lastline.split(b"/")[4])
            else:
                logging.debug("last line of ping did not contain timings: " + repr(lastline))
                rtt = None
            self.push(rtt)
        except Exception as e:
            logging.exception(" ".join([
                type(e).__name__ + ":",
                str(e),
                "in Ping for \"{host}\"".format(host=host)
            ]))
