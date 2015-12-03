import logging
import subprocess

from .base import TimedSource



class SNMPGet(TimedSource):

    def snmpcall(self, host, oid, version=1, community="public"):
        args = [
            "snmpget",
            "-O", "q",
            "-v", str(version),
            "-c", str(community),
            str(host),
            str(oid)
        ]
        process = subprocess.Popen(args, stdout=subprocess.PIPE)
        out, err = process.communicate()
        return out

    def poll(self):
        host = self.get_config("host")
        oid = self.get_config("oid")
        version = self.get_config("version", 1)
        community = self.get_config("community", "public")
        try:
            out = self.snmpcall(host, oid, version, community)
            line = out.split(b"\n")[0]
            if line:
                value = line.split(b" ")[1].decode("utf-8")
                value = self.typecast(value)
                self.push(value)
        except Exception as e:
            logging.exception(" ".join([
                type(e).__name__ + ":",
                str(e),
                "in SNMPGet for \"{name}\"".format(name=self.get_config("name"))
            ]))



class SNMPWalkSum(TimedSource):

    def snmpcall(self, host, oid, version=1, community="public"):
        args = [
            "snmpbulkwalk",
            "-O", "q",
            "-v", str(version),
            "-c", str(community),
            str(host),
            str(oid)
        ]
        process = subprocess.Popen(args, stdout=subprocess.PIPE)
        out, err = process.communicate()
        return out

    def poll(self):
        host = self.get_config("host")
        oid = self.get_config("oid")
        version = self.get_config("version", 1)
        community = self.get_config("community", "public")
        try:
            out = self.snmpcall(host, oid, version, community)
            total = 0
            for line in out.split(b"\n"):
                if line:
                    value = self.typecast(line.split(b" ")[1].decode("utf-8"))
                    total += value
            self.push(total)
        except Exception as e:
            logging.exception(" ".join([
                type(e).__name__ + ":",
                str(e),
                "in SNMPWalkSum for \"{name}\"".format(name=self.get_config("name"))
            ]))
