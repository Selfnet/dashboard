import socket
import logging

from .base import TimedSource



class Munin(TimedSource):

    def get_value(self, key, output):
        for line in output.split("\n"):
            if line.startswith(key + ".value "):
                start = len(key) + len(".value ")
                return line[start:]

    def poll(self):
        host = self.get_config("host", "localhost")
        port = self.get_config("port", 4949)
        timeout = self.get_config("timeout", 5)
        module = self.get_config("module")
        key = self.get_config("key")

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
            self.push(value)
        except Exception as e:
            logging.error(" ".join([
                    type(e).__name__ + ":",
                    str(e),
                    "in Munin for \"{name}\"".format(name=self.get_config("name"))
            ]))
