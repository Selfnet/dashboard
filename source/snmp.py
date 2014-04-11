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

    def snmpcall(self):
        args = [
            "snmpget",
            "-O", "q",
            "-v", str(self.params["version"]),
            "-c", str(self.params["community"]),
            str(self.params["host"]),
            str(self.params["oid"])
        ]
        process = subprocess.Popen(args, stdout=subprocess.PIPE)
        out, err = process.communicate()
        return out

    def poll(self):
        try:
            out = self.snmpcall()
        except Exception as e:
            logging.error(" ".join([
                type(e).__name__ + ":",
                str(e),
                "in SNMPGet SNMP-call for \"" + self.params["host"] + "\", OID: \"" + self.params["oid"] + "\""
            ]))

        if out:
            try:
                line = out.split(b"\n")[0]
                if line:
                    typecast = self.params["typecast"]
                    value = line.split(b" ")[1]
                    if typecast:
                        value = typecast(value)
                    self.push(self.params["name"], value)
            except Exception as e:
                logging.error(" ".join([
                    type(e).__name__ + ":",
                    str(e),
                    "in SNMPGet for \"" + self.params["host"] + "\", OID: \"" + self.params["oid"] + "\""
                ]))



class SNMPWalkSum(TimedSource):

    defaults = {
        "version": 1,
        "community": "public",
        "typecast": int,
    }

    required = [
        "host",
        "oid",
        "name",
    ]

    def snmpcall(self):
        args = [
            "snmpbulkwalk",
            "-O", "q",
            "-v", str(self.params["version"]),
            "-c", str(self.params["community"]),
            str(self.params["host"]),
            str(self.params["oid"])
        ]
        process = subprocess.Popen(args, stdout=subprocess.PIPE)
        out, err = process.communicate()
        return out

    def poll(self):
        try:
            out = self.snmpcall()
        except Exception as e:
            logging.error(" ".join([
                type(e).__name__ + ":",
                str(e),
                "in SNMPWalkSum for \"" + self.params["host"] + "\", OID: \"" + self.params["oid"] + "\""
            ]))

        if out:
            total = 0
            typecast = self.params["typecast"]
            try:
                for line in out.split(b"\n"):
                    if line:
                        value = typecast(line.split(b" ")[1])
                        total += value
                self.push(self.params["name"], total)
            except Exception as e:
                logging.error(" ".join([
                    type(e).__name__ + ":",
                    str(e),
                    "in SNMPWalkSum for \"" + self.params["host"] + "\", OID: \"" + self.params["oid"] + "\""
                ]))
