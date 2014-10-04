import logging
import builtins
import subprocess # ever tried urllib in python3 on debian stable?

from .base import TimedSource



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
            type_name = self.get_config("typecast", "str")
            try:
                typecast = getattr(builtins, type_name)
                if not isinstance(typecast, type):
                    raise ValueError("not a type")
            except ValueError:
                raise Exception("HTTPGet: invalid type cast (not a built-in type)")
            value = typecast(out)
            self.push(self.get_config("name"), value)
        except Exception as e:
            logging.error(" ".join([
                type(e).__name__ + ":",
                str(e),
                "in HTTPGet for \"" + url + "\""
            ]))
