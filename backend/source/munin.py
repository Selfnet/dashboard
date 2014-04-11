import socket
import logging

from base import TimedSource



class Munin(TimedSource):

    defaults = {
        "timeout": 3,
        "port": 4949,
    }

    required = [
        "module",
        "key",
        "host",
    ]

    def get_value(self, key, output):
        for line in output.split("\n"):
            if line.startswith(key + ".value "):
                return int(line.split(" ")[1])

    def poll(self):
        host = self.params["host"]
        port = self.params["port"]
        timeout = self.params["timeout"]
        module = self.params["module"]
        name = self.params["name"]
        key = self.params["key"]

        try:
            s = socket.create_connection((host, port), timeout)
            s.settimeout(timeout)
            cmd = ("fetch " + module + "\nquit").encode("ascii")
            s.send(cmd)
            result = ""
            while True:
                output, addr = s.recvfrom(2048)
                result += output.decode("utf-8")
                if result.endswith("\n.\n"):
                    break
                if not output:
                    break
            value = self.get_value(key, result)
            self.push(name, value)
        except Exception as e:
            logging.error(" ".join([
                    type(e).__name__ + ":",
                    str(e),
                    "in Munin for \"" + self.params["name"]
            ]))
