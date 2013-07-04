from threading import Lock


class Source(object):
    dependencies = []
    def __init__(self, name):
        self.name = name

    def configure(self, data, defaults, interval):
        self.data = data
        self.data.add_set(self.name)
        


class Data():
    def __init__(self, maxlength):
        self.datasets = {}
        self.maxlength = maxlength
        self.lock = Lock()

    def get_dataset(self, name):
        try:
            return self.datasets[name]
        except KeyError:
            self.add_set(name)
            return self.datasets[name]

    def add_set(self, name):
        self.lock.acquire()
        self.datasets[name] = []
        self.lock.release()

    def has_set(self, name):
        if name in self.datasets:
            return True
        return False

    def add(self, name, value):
        dataset = self.get_dataset(name)
        self.lock.acquire()
        dataset.append(value)
        if len(dataset) > self.maxlength:
            dataset.pop(0)
        self.lock.release()

