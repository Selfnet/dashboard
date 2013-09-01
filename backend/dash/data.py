from threading import Lock


class Source(object):
    dependencies = []
    def __init__(self, name):
        self.name = name

    def configure(self, data, defaults, interval):
        self.data = data
        self.data.add_set(self.name)



class Dataset():
    def __init__(self, length):
        self.length = length
        self.dataset = []
        self.lock = Lock()

    def add(self, value):
        self.lock.acquire()
        self.dataset.append(value)
        if len(self.dataset) > self.length:
            self.dataset.pop(0)
        self.lock.release()

    def get(self, i):
        """ get a list entry """
        return self.dataset[i]

    def get_list(self):
        return self.dataset

    def latest_value(self):
        """ returns the latest added value != None """
        # doesn't need to be locked, since dataset reads
        # usually happen *after* new data from sources was fetched
        # TODO catch IndexError

        a = None
        i = 1
        while a == None:
            a = self.dataset[-i]
            i += 1
        return a

    def two_latest_values(self):
        """ returns the two latest added values != None """
        # doesn't need to be locked, since dataset reads
        # usually happen *after* new data from sources was fetched
        # TODO catch IndexError

        a = None # first value
        b = None # second (most recent) value
        i = 1
        while b == None:
            b = self.dataset[-i]
            i += 1
        # found b
        while a == None:
            a = self.dataset[-i]
            i += 1
        # found a
        return a,b




class Data():
    def __init__(self, config):
        self.datasets = {}
        self.config = config
        self.lock = Lock()

    def get_dataset(self, name):
        try:
            return self.datasets[name]
        except KeyError:
            self.add_set(name)
            return self.datasets[name]

    def add_set(self, name, length=None):
        # use default length?
        if not length:
            length = self.config.defaults["dataset size"]
        self.lock.acquire()
        self.datasets[name] = Dataset(length)
        self.lock.release()

    def has_set(self, name):
        if name in self.datasets:
            return True
        return False

    def add(self, name, value):
        dataset = self.get_dataset(name)
        dataset.add(value)


