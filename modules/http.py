import logging
import subprocess # ever tried urllib in python3 on debian stable?

from .base.sources import TimedSource



class HTTPGet(TimedSource):

    def curlcall(self, url):
        args = [
            "curl",
            "--silent",
            str(url)
        ]
        process = subprocess.Popen(args, stdout=subprocess.PIPE)
        out, err = process.communicate()
        return out

    def poll(self):
        url = self.get_config("url")
        try:
            out = self.curlcall(url)
            value = self.typecast(out.strip())
            self.push(value)
        except Exception as e:
            logging.exception(" ".join([
                type(e).__name__ + ":",
                str(e),
                "in HTTPGet for \"" + url + "\""
            ]))
