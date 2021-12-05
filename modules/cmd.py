import logging
import asyncio

from .base.sources import TimedSource



class Cmd(TimedSource):

    async def cmdcall(self, args):
        process = await asyncio.create_subprocess_shell(args, stdout=asyncio.subprocess.PIPE)
        out, err = await process.communicate()
        if isinstance(out, bytes): out = out.decode("utf-8")
        return out

    async def poll(self):
        cmd = self.get_config("command")
        try:
            out = await self.cmdcall(cmd)
            self.push(out.strip())
        except Exception as e:
            logging.exception(" ".join([
                type(e).__name__ + ":",
                str(e),
                "in Cmd for \"{name}\"".format(name=self.get_config("name"))
            ]))
