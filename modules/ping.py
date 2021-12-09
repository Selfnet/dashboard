import logging
import asyncio
import datetime

from .base.sources import TimedSource


class Ping(TimedSource):

    async def pingcall(self, host, count=1, timeout=1, protocol=4):
        if protocol == 4:
            cmd = "ping"
        else:
            cmd = "ping6"
        args = [
            cmd,
            "-c", "1",
            "-i", "0.2",
            "-c", str(count),
            "-W", str(timeout),
            str(host)
        ]
        process = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE)
        out, err = await process.communicate()
        return out

    async def poll(self):
        host = self.get_config("host")
        count = self.get_config("count", 1)
        timeout = self.get_config("timeout", 1)
        protocol = self.get_config("protocol", 4)
        logging.warning(datetime.datetime.now().isoformat() + ': Starting Ping to host ' + host)
        if protocol == 6 or str(protocol)[-1] == "6":
            protocol = 6
        else:
            protocol = 4
        try:
            out = await self.pingcall(host, count, timeout, protocol)
            lastline = out.strip().split(b"\n")[-1]
            if lastline.startswith(b"rtt min/avg/max/mdev = "):
                rtt = float(lastline.split(b"/")[4])
            else:
                logging.debug("last line of ping did not contain timings: " + repr(lastline))
                rtt = None
            await self.push(rtt)
        except Exception as e:
            logging.exception(" ".join([
                type(e).__name__ + ":",
                str(e),
                "in Ping for \"{host}\"".format(host=host)
            ]))
        logging.warning(datetime.datetime.now().isoformat() + ': Finished Ping to host ' + host)
