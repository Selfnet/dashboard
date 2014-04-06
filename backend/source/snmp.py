from base import OriginalSource

class SNMP(OriginalSource):

    defaults = {
        "version": 1,
        "community": "public",
    }

    required = [
        "host",
        "oid",
        "name",
    ]

    def poll(self):
        # TODO do SNMP magic here
        self.push(self.name, 42)
