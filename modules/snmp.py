import logging
import asyncio
import datetime
from .base.sources import TimedSource


class SNMPGet(TimedSource):

    async def snmpcall(self, host, oid, version=1, community="public"):
        args = [
            "snmpget",
            "-O", "q",
            "-v", str(version),
            "-c", str(community),
            str(host),
            str(oid)
        ]
        process = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        out, err = await process.communicate()
        print(datetime.datetime.now().isoformat() + ' SNMPGet ' + out.decode('utf-8') + ' Error: ' + err.decode('utf-8'))
        return out

    async def poll(self):
        host = self.get_config("host")
        oid = self.get_config("oid")
        version = self.get_config("version", 1)
        community = self.get_config("community", "public")
        try:
            out = await self.snmpcall(host, oid, version, community)
            line = out.split(b"\n")[0]
            if line:
                value = line.split(b" ")[1].decode("utf-8")
                value = self.typecast(value)
                await self.push(value)
        except Exception as e:
            logging.exception(" ".join([
                type(e).__name__ + ":",
                str(e),
                "in SNMPGet for \"{name}\"".format(name=self.get_config("name"))
            ]))



class SNMPWalkSum(TimedSource):

    async def snmpcall(self, host, oid, version=1, community="public"):
        args = [
            "snmpbulkwalk",
            "-O", "q",
            "-v", str(version),
            "-c", str(community),
            str(host),
            str(oid)
        ]
        process = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        out, err = await process.communicate()
        print(datetime.datetime.now().isoformat() + ' SNMPWalk ' + out.decode('utf-8') + ' Error: ' + err.decode('utf-8'))
        return out

    async def poll(self):
        host = self.get_config("host")
        oid = self.get_config("oid")
        version = self.get_config("version", 1)
        community = self.get_config("community", "public")
        try:
            out = await self.snmpcall(host, oid, version, community)
            total = 0
            for line in out.split(b"\n"):
                if line:
                    value = self.typecast(line.split(b" ")[1].decode("utf-8"))
                    total += value
            await self.push(total)
        except Exception as e:
            logging.exception(" ".join([
                type(e).__name__ + ":",
                str(e),
                "in SNMPWalkSum for \"{name}\"".format(name=self.get_config("name"))
            ]))
