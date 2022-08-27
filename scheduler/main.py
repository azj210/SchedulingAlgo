import sys
from process import Process
from myRandom import Random


def remove_values_from_list(the_list, val):
    while val in the_list:
        the_list.remove(val)


def print_debug_info(clock, list_len, process_list, ready_list, block_list, end_list, running_process):
    out = "Before cycle %4d:" % clock
    for index in range(list_len):
        for p in process_list:
            if p.order == index:
                out += " %11s %d" % ("unstarted", 0)

        for p in ready_list:
            if p.order == index:
                out += " %11s %d" % ("ready", 0)

        for p in block_list:
            if p.order == index:
                out += " %11s %d" % ("blocked", p.cur_io_time)

        for p in end_list:
            if p.order == index:
                out += " %11s %d" % ("terminated", 0)

        if running_process is not None and running_process.order == index:
            out += " %11s %d" % ("running", running_process.cur_cpu_time)

    print(out + ".")


def print_end_list(cpu_use, end_list, total_clock):
    end_list.sort(key=lambda x: x.order)
    index = 0
    total_waiting_time = 0
    total_turnaround_time = 0
    io_use = 0
    for process in end_list:
        print("Process " + str(index) + ":")
        print("\t(A,B,C,IO) = (%d,%d,%d,%d)" % (process.A, process.B, process.C, process.IO))
        print("\tFinishing time: " + str(process.switch_clock))
        print("\tTurnaround time: " + str(process.switch_clock - process.A))
        print("\tI/O time: " + str(process.io_time))
        print("\tWaiting time: " + str(process.wait_time))
        print()
        total_waiting_time += process.wait_time
        total_turnaround_time += process.switch_clock - process.A
        io_use += process.io_time
        index += 1

    print("Summary Data:")
    print("\tFinishing time: " + str(total_clock))
    print("\tCPU Utilization: %.6f" % (float(cpu_use) / float(total_clock)))
    print("\tI/O Utilization: %.6f" % (float(io_use) / float(total_clock)))
    print("\tThroughput: %.6f processes per hundred cycles" % (float(len(end_list)) * float(100) / float(total_clock)))
    print("\tAverage turnaround time: %.6f" % (float(total_turnaround_time) / float(len(end_list))))
    print("\tAverage waiting time: %.6f" % (float(total_waiting_time) / float(len(end_list))))


def run_rr(process_list, show_info):
    list_len = len(process_list)
    random = Random()
    ready_list = []
    block_list = []
    end_list = []
    running_process = None
    clock = 0
    cpu_use = 0
    rr_time = 2
    print("The scheduling algorithm used was Round Robin with quantum of 2\n")
    while True:
        if show_info:
            print_debug_info(clock, list_len, process_list, ready_list, block_list, end_list, running_process)


        for p in block_list[:]:
            if p.cur_io_time > 0:
                p.cur_io_time -= 1
            if p.cur_io_time <= 0:
                p.in_ready_time = 0
                ready_list.append(p)
                block_list.remove(p)


        for p in process_list[:]:
            if p.switch_clock <= clock:
                p.in_ready_time = 0
                ready_list.append(p)
                process_list.remove(p)

        if running_process is not None:
            running_process.cur_cpu_time -= 1
            cpu_use += 1


        if running_process is not None and running_process.cur_cpu_time <= 0:
            if running_process.cpu_total_time == 0:
                end_list.append(running_process)
            else:
                running_process.io_burst(clock, random)
                block_list.append(running_process)
            running_process = None


        if running_process is not None and rr_time <= 0:
            # running_process.io_burst(clock, random)
            running_process.in_ready_time = 0
            ready_list.append(running_process)
            running_process = None


        ready_list.sort(key=lambda x: (-x.in_ready_time, x.A, x.order))
        for p in ready_list[:]:
            if p.cur_cpu_time >= 0 or (p.A <= clock and p.cur_cpu_time == -1 and p.cur_io_time == -1):
                if running_process is None:
                    p.rr_cpu_burst(clock, random)
                    ready_list.remove(p)
                    running_process = p
                    rr_time = 2
                else:
                    p.wait()
            p.in_ready_time += 1

        if len(ready_list) == 0 and len(block_list) == 0 and running_process is None:
            break

        clock += 1
        rr_time -= 1
    print_end_list(cpu_use, end_list, clock)


def run_uni(process_list, show_info):
    list_len = len(process_list)
    random = Random()
    print("The scheduling algorithm used was Uniprocessor\n")
    running_process = None
    end_list = []
    cpu_use = 0
    clock = 0
    to_running = 0  # 2 running 1 blocked 0 null
    is_switch = False

    while True:
        if show_info:
            out = "Before cycle %4d:" % clock
            for index in range(list_len):
                for p in process_list:
                    if p.order == index:
                        out += " %11s %d" % ("unstarted", 0)

                if running_process is not None and running_process.order == index:
                    if to_running:
                        out += " %11s %d" % ("running", running_process.cur_cpu_time)
                    else:
                        out += " %11s %d" % ("blocked", running_process.cur_io_time)

                for p in end_list:
                    if p.order == index:
                        out += " %11s %d" % ("terminated", 0)



            print(out + ".")

        if running_process is not None and running_process.switch_clock <= clock and running_process.cpu_total_time == 0:
            end_list.append(running_process)
            running_process = None
            # to_running = False


        if to_running == 2:
            cpu_use += 1


        if running_process is not None and running_process.switch_clock <= clock and running_process.cpu_total_time > 0:
            if to_running != 2:
                running_process.cpu_burst(clock, random)
                to_running = 2
            else:
                running_process.io_burst(clock, random)
                to_running = 1


        for p in process_list[:]:
            if p.A <= clock:
                if running_process is None:
                    running_process = p
                    process_list.remove(p)
                    to_running = 0
                    is_switch = True
                    break
                else:

                    p.wait()


        if is_switch:
            is_switch = False
            continue

        if len(process_list) == 0 and running_process is None:
            break

        clock += 1
    print_end_list(cpu_use, end_list, clock)


def run_sjf(process_list, show_info):
    list_len = len(process_list)
    random = Random()
    ready_list = []
    block_list = []
    end_list = []
    running_process = None
    clock = 0
    cpu_use = 0
    print("The scheduling algorithm used was Shortest Job First\n")
    while True:
        if show_info:
            print_debug_info(clock, list_len, process_list, ready_list, block_list, end_list, running_process)

        for p in block_list[:]:
            if p.switch_clock <= clock:
                ready_list.append(p)
                block_list.remove(p)
            else:
                p.cur_io_time -= 1


        for p in process_list[:]:
            if p.A <= clock:
                ready_list.append(p)
                process_list.remove(p)


        if running_process is not None and running_process.switch_clock <= clock:
            if running_process.cpu_total_time == 0:
                end_list.append(running_process)
            else:
                running_process.io_burst(clock, random)
                block_list.append(running_process)
            running_process = None

        if running_process is not None:
            #
            running_process.cur_cpu_time -= 1

        ready_list.sort(key=lambda x: (x.cpu_total_time, x.order))


        for p in ready_list[:]:
            if p.switch_clock <= clock:
                if running_process is None:
                    p.cpu_burst(clock, random)
                    ready_list.remove(p)
                    running_process = p
                else:
                    p.wait()

        if len(ready_list) == 0 and len(block_list) == 0 and running_process is None:
            break

        if running_process is not None:
            cpu_use += 1
        clock += 1

    print_end_list(cpu_use, end_list, clock)


def run_fcfs(process_list, show_info):
    list_len = len(process_list)
    random = Random()
    ready_list = []
    block_list = []
    end_list = []
    running_process = None
    clock = 0
    cpu_use = 0
    while True:
        if show_info:
            print_debug_info(clock, list_len, process_list, ready_list, block_list, end_list, running_process)

        for p in block_list[:]:
            if p.switch_clock <= clock:
                ready_list.append(p)
                block_list.remove(p)
            else:
                p.cur_io_time -= 1


        for p in process_list[:]:
            if p.A <= clock:
                ready_list.append(p)
                process_list.remove(p)


        if running_process is not None and running_process.switch_clock <= clock:
            if running_process.cpu_total_time == 0:
                end_list.append(running_process)
            else:
                running_process.io_burst(clock, random)
                block_list.append(running_process)
            running_process = None

        if running_process is not None:
            running_process.cur_cpu_time -= 1


        ready_list.sort(key=lambda x: (x.switch_clock, x.order))


        for p in ready_list[:]:
            if p.switch_clock <= clock:
                if running_process is None:
                    p.cpu_burst(clock, random)
                    ready_list.remove(p)
                    running_process = p
                else:
                    p.wait()


        if len(ready_list) == 0 and len(block_list) == 0 and running_process is None:
            break

        if running_process is not None:
            cpu_use += 1

        clock += 1
    print("The scheduling algorithm used was First Come First Served\n")
    print_end_list(cpu_use, end_list, clock)


#ShowInfo = True

input_now = input("which file to use?")
to_split = input_now.split(" ")
if len(to_split) > 1:
    input_filename = to_split[1]
else:
    input_filename = to_split[0]
if ("--verbose" in input_now):
    ShowInfo = True
else:
    ShowInfo = False
    
if len(sys.argv) == 3:
    input_filename = sys.argv[2]
    if sys.argv[1].count("verbose") > 0:
        ShowInfo = True

elif len(sys.argv) == 2:
    input_filename = sys.argv[1]
else:
    print("Input start")

ReadyList = []
BlockList = []


def list_to_string(list):
    str = ""
    for item in list:
        str += "  "
        str += item.__str__()
    return str



def read_data_and_run(simu):
    with open(input_filename) as file:
        line = file.readline()
        parms = line.split(" ")
        n = int(parms[0])
        remove_values_from_list(parms, '')
        parms.pop(0)

        for i in range(n):
            index = i * 4
            process = Process(parms[index], parms[index + 1], parms[index + 2], parms[index + 3])
            ReadyList.append(process)


        origin_str = "The original input is:  " + str(n) + list_to_string(ReadyList)
        ReadyList.sort(key=lambda x: x.A)
        sorted_str = "The (sorted) input was: " + str(n) + list_to_string(ReadyList)

        order = 0
        for p in ReadyList[:]:
            p.order = order
            order += 1

        print(origin_str)
        print(sorted_str)
        print()
    simu(ReadyList, ShowInfo)


read_data_and_run(run_fcfs)
print("**********************\n")
read_data_and_run(run_rr)
print("**********************\n")
read_data_and_run(run_uni)
print("**********************\n")
read_data_and_run(run_sjf)
print("**********************\n")

