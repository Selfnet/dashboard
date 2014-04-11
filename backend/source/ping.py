import logging
import subprocess # ever tried urllib in python3 on debian stable?

from base import TimedSource



class Ping(TimedSource):

    defaults = {
        "timeout": 1,
        "count": 1,
    }

    required = [
        "host",
        "name",
    ]

    def pingcall(self):
        args = [
            "ping",
            "-c", "1",
            "-i", "0.2",
            "-c", str(self.params["count"]),
            "-W", str(self.params["timeout"]),
            str(self.params["host"])
        ]
        process = subprocess.Popen(args, stdout=subprocess.PIPE)
        out, err = process.communicate()
        return out

    def poll(self):
        name = self.params["name"]
        try:
            out = self.pingcall()
            lastline = out.strip().split(b"\n")[-1]
            if lastline.startswith(b"rtt min/avg/max/mdev = "):
                rtt = float(lastline.split(b"/")[4])
            else:
                logging.debug("last line of ping did not contain timings: " + repr(lastline))
                rtt = None
            self.push(name, rtt)
        except Exception as e:
            logging.error(" ".join([
                type(e).__name__ + ":",
                str(e),
                "in Ping for \"" + self.params["host"] + "\""
            ]))
