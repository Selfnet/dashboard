import logging
import subprocess

from .base.sources import TimedSource



class Cmd(TimedSource):

    def cmdcall(self, args):
        process = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True)
        out, err = process.communicate()
        if isinstance(out, bytes): out = out.decode("utf-8")
        return out

    def poll(self):
        cmd = self.get_config("command")
        try:
            out = self.cmdcall(cmd)
            self.push(out.strip())
        except Exception as e:
            logging.exception(" ".join([
                type(e).__name__ + ":",
                str(e),
                "in Cmd for \"{name}\"".format(name=self.get_config("name"))
            ]))
