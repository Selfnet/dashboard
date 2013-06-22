from threading import Lock


class Source(object):
    def configure(self, data, defaults, interval):
        self.data = data


class Data():
    def __init__(self, maxlength):
        self.datasets = {}
        self.maxlength = maxlength
        self.lock = Lock()

    def get_dataset(self, name):
        try:
            return self.datasets[name]
        except KeyError:
            self.lock.acquire()
            self.datasets[name] = []
            self.lock.release()
            return self.datasets[name]

    def add(self, name, value):
        dataset = self.get_dataset(name)
        self.lock.acquire()
        dataset.append(value)
        if len(dataset) > self.maxlength:
            dataset.pop(0)
        self.lock.release()

