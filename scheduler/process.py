class Process:
    def __init__(self, A, B, C, IO):
        self.A = int(A)
        self.B = int(B)
        self.C = int(C)
        self.IO = int(IO)
        self.cpu_total_time = self.C
        self.switch_clock = self.A
        self.wait_time = 0
        self.io_time = 0
        self.order = -1
        self.cur_cpu_time = -1
        self.cur_io_time = -1
        self.in_ready_time = -1

    def __str__(self):
        # return "%d %d %d %d" % (self.A, self.B, self.C, self.IO)
        return "%d %d %d %d" % (self.order, self.cur_cpu_time, self.cur_io_time, self.switch_clock)

    def __repr__(self):
        return self.__str__()

    def cpu_burst(self, clock, random):
        self.cur_cpu_time = random.randomOS(self.B)
        if self.cur_cpu_time > self.cpu_total_time:
            self.cur_cpu_time = self.cpu_total_time
        self.cpu_total_time -= self.cur_cpu_time
        self.switch_clock = clock + self.cur_cpu_time

    def io_burst(self, clock, random):
        self.cur_io_time = random.randomOS(self.IO)
        self.io_time += self.cur_io_time
        self.switch_clock = clock + self.cur_io_time

    def rr_cpu_burst(self, clock, random):
        if self.cur_cpu_time > 0:
            return
        self.cur_cpu_time = random.randomOS(self.B)
        if self.cur_cpu_time > self.cpu_total_time:
            self.cur_cpu_time = self.cpu_total_time
        self.cpu_total_time -= self.cur_cpu_time
        self.switch_clock = clock + self.cur_cpu_time

    def wait(self):
        self.wait_time += 1
