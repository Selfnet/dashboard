import logging
import subprocess # ever tried urllib in python3 on debian stable?

from base import TimedSource



class HTTPGet(TimedSource):

    defaults = {
        "typecast": None
    }

    required = [
        "url",
        "name",
    ]

    def curlcall(self):
        args = [
            "curl",
            "--silent",
            str(self.params["url"])
        ]
        process = subprocess.Popen(args, stdout=subprocess.PIPE)
        out, err = process.communicate()
        return out

    def poll(self):
        try:
            out = self.curlcall()
            typecast = self.params["typecast"]
            if typecast:
                value = typecast(out)
            else:
                value = out
            self.push(self.params["name"], value)
        except Exception as e:
            logging.error(" ".join([
                type(e).__name__ + ":",
                str(e),
                "in HTTPGet for \"" + self.params["url"] + "\""
            ]))
