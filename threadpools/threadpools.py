import sys
import queue
import threading


class Worker(threading.Thread):
    def __init__(self, in_queue, out_queue, err_queue):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.err_queue = err_queue
        self.start()

    def run(self):
        while True:
            command, callback, args, kwds = self.in_queue.get()
            if command == "stop":
                break
            try:
                if command != "process":
                    raise "Unknown command {}".format(command)
            except:
                self.report_error()
            else:
                self.out_queue.put(callback(*args, **kwds))

    def dismiss(self):
        command = "stop"
        self.in_queue.put((command, None, None, None))

    def report_error(self):
        self.err_queue.put(sys.exc_info()[:2])


class ThreadPools:

    max_threads = 32

    def __init__(self, num_threads, pool_size=0):
        num_threads = (
            ThreadPools.max_threads
            if num_threads > ThreadPools.max_threads
            else num_threads
        )
        self.in_queue = queue.Queue(pool_size)
        self.out_queue = queue.Queue(pool_size)
        self.err_queue = queue.Queue(pool_size)
        self.workers = {}
        for i in range(num_threads):
            worker = Worker(self.in_queue, self.out_queue, self.err_queue)
            self.workers[i] = worker

    def map(self, func, args_list):
        for args in args_list:
            self.add_task(func, args)

    def add_task(self, callback, *args, **kwds):
        command = "process"
        self.in_queue.put((command, callback, args, kwds))

    def _get_results(self, queue):
        try:
            while True:
                yield queue.get_nowait()
        except queue.Empty:
            raise StopIteration

    def get_task(self):
        return self.out_queue.get()

    def show_results(self):
        for result in self._get_results(self.out_queue):
            print("Result:", result)

    def show_errors(self):
        for etyp, err in self._get_results(self.err_queue):
            print("Error:", etyp, err)

    def destroy(self):
        for i in self.workers:
            self.workers[i].dismiss()
        for i in self.workers:
            self.workers[i].join()
        del self.workers
