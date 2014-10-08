import logging
import subprocess # ever tried urllib in python3 on debian stable?

from .base import TimedSource



class Ping(TimedSource):

    def pingcall(self, host, count=1, timeout=1):
        args = [
            "ping",
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
        try:
            out = self.pingcall(host, count, timeout)
            lastline = out.strip().split(b"\n")[-1]
            if lastline.startswith(b"rtt min/avg/max/mdev = "):
                rtt = float(lastline.split(b"/")[4])
            else:
                logging.debug("last line of ping did not contain timings: " + repr(lastline))
                rtt = None
            self.push(rtt)
        except Exception as e:
            logging.error(" ".join([
                type(e).__name__ + ":",
                str(e),
                "in Ping for \"{host}\"".format(host=host)
            ]))
