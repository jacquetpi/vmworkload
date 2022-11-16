import random
import math

class VmSliceWorkload(object):

    TOOL_FOLDER = "/usr/local/src/vmworkload/tools/"
    SSH_FORMAT = "sshvm.sh {name} \"{data}\""

    def generate_workload_with_peak(self, vm_name : str, slice_duration : int, workload_cpu_avg : int, workload_cpu_per : int):
        return "not implemented"

    def generate_workload(self, vm_name : str, slice_duration : int, workload_cpu_avg : int):
        return "not implemented"

class VmSliceWorkloadIdle(VmSliceWorkload):

    def generate_workload_with_peak(self, vm_name : str, slice_duration : int, workload_cpu_avg : int, workload_cpu_per : int):
        peak_duration = 10
        random_input = random.randrange(0,slice_duration-peak_duration)
        data =   "sleep " + str(random_input) +  " ; " +\
                "stress-ng --timeout " + str(peak_duration) + " -c 0 -l " + str(workload_cpu_per) + " ; " +\
                "sleep " + str(slice_duration-random_input-peak_duration) + " ; "
        return VmSliceWorkload.TOOL_FOLDER + VmSliceWorkload.SSH_FORMAT.replace("{name}", vm_name).replace("{data}", data) + " ; "

    def generate_workload(self, vm_name : str, slice_duration : int, workload_cpu_avg : int):
        data =  "sleep " + str(slice_duration) +  " ; "
        return VmSliceWorkload.TOOL_FOLDER + VmSliceWorkload.SSH_FORMAT.replace("{name}", vm_name).replace("{data}", data) + " ; "

class VmSliceWorkloadStressNG(VmSliceWorkload):

    def generate_workload_with_peak(self, vm_name : str, slice_duration : int, workload_cpu_avg : int, workload_cpu_per : int):
        peak_duration = 10
        random_input = random.randrange(0,slice_duration-peak_duration)
        data =   "stress-ng --timeout " + str(random_input) +  " -c 0 -l " + str(workload_cpu_avg) + " ; " +\
                "stress-ng --timeout " + str(peak_duration) + " -c 0 -l " + str(workload_cpu_per) + " ; " +\
                "stress-ng --timeout " + str(slice_duration-random_input-peak_duration) +  " -c 0 -l " + str(workload_cpu_avg) + " ; "
        return VmSliceWorkload.TOOL_FOLDER + VmSliceWorkload.SSH_FORMAT.replace("{name}", vm_name).replace("{data}", data) + " ; "

    def generate_workload(self, vm_name : str, slice_duration : int, workload_cpu_avg : int):
        data =  "stress-ng --timeout " + str(slice_duration) +  " -c 0 -l " + str(workload_cpu_avg) + " ; "
        return VmSliceWorkload.TOOL_FOLDER + VmSliceWorkload.SSH_FORMAT.replace("{name}", vm_name).replace("{data}", data) + " ; "

class VmSliceWorkloadWordpress(VmSliceWorkload):

    def generate_workload(self, vm_name : str, slice_duration : int, workload_cpu_avg : int):
        return VmSliceWorkload.TOOL_FOLDER + "siege.sh " + vm_name + " " + str(slice_duration) + " " + str(math.ceil(workload_cpu_avg/10)) + " ; "

class VmSliceWorkloadDeathStarBench(VmSliceWorkload):

    def generate_workload(self, vm_name : str, slice_duration : int, workload_cpu_avg : int):
        return VmSliceWorkload.TOOL_FOLDER + "wrk2.sh " + vm_name + " " + str(slice_duration) + " " + str(math.ceil(workload_cpu_avg*100)) + " ; "

class VmSliceWorkloadTpcc(VmSliceWorkload):

    def generate_workload(self, vm_name : str, slice_duration : int, workload_cpu_avg : int):
        thresold = math.ceil(workload_cpu_avg*100)
        if thresold>20000:
            thresold = 20000
        return VmSliceWorkload.TOOL_FOLDER + "tpcc.sh " + vm_name + " " + str(slice_duration) + " " + str(thresold) + " ; "

class VmSliceWorkloadTpch(VmSliceWorkload):

    def generate_workload(self, vm_name : str, slice_duration : int, workload_cpu_avg : int):
        return VmSliceWorkload.TOOL_FOLDER + "tpch.sh " + vm_name + " " + str(math.ceil(workload_cpu_avg*100)) + " ; "