import logging
import subprocess

from base import TimedSource



class SNMPGet(TimedSource):

    defaults = {
        "version": 1,
        "community": "public",
        "typecast": None
    }

    required = [
        "host",
        "oid",
        "name",
    ]

    def poll(self):
        args = [
            "snmpget",
            "-O", "q",
            "-v", str(self.params["version"]),
            "-c", str(self.params["community"]),
            str(self.params["host"]),
            str(self.params["oid"])
        ]

        try:
            process = subprocess.Popen(args, stdout=subprocess.PIPE)
            out, err = process.communicate()
        except Exception as e:
            logging.error(" ".join([
                type(e).__name__ + ":",
                str(e),
                "in SNMPGet for \"" + self.params["host"] + "\", OID: \"" + self.params["oid"] + "\""
            ]))
            self.push(self.name, None)

        try:
            if out:
                line = out.split(b"\n")[0]
                if line:
                    typecast = self.params["typecast"]
                    value = line.split(b" ")[1]
                    if typecast:
                        value = typecast(value)
                self.push(self.name, value)
            else:
                self.push(self.name, None)
        except Exception as e:
            logging.error(" ".join([
                type(e).__name__ + ":",
                str(e),
                "in SNMPGet for \"" + self.params["host"] + "\", OID: \"" + self.params["oid"] + "\""
            ]))
            self.push(self.name, None)
