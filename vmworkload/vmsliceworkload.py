import random

class VmSliceWorkload(object):

    def generate_workload_with_peak(self, slice_duration : int, workload_cpu_avg : int, workload_cpu_per : int):
        return "not implemented"

    def generate_workload(self, slice_duration : int, workload_cpu_avg : int):
        return "not implemented"

class VmSliceWorkloadIdle(VmSliceWorkload):

    def generate_workload_with_peak(self, slice_duration : int, workload_cpu_avg : int, workload_cpu_per : int):
        peak_duration = 10
        random_input = random.randrange(0,slice_duration-peak_duration)
        cmd = "sleep " + str(random_input) +  " ; " +\
            "stress-ng --timeout " + str(peak_duration) + " -c 0 -l " + str(workload_cpu_per) + " ; " +\
            "sleep " + str(slice_duration-random_input-peak_duration) + " ; "
        return cmd

    def generate_workload(self, slice_duration : int, workload_cpu_avg : int):
        return "sleep " + str(slice_duration) +  " ; "

class VmSliceWorkloadStressNG(VmSliceWorkload):

    def generate_workload_with_peak(self, slice_duration : int, workload_cpu_avg : int, workload_cpu_per : int):
        peak_duration = 10
        random_input = random.randrange(0,slice_duration-peak_duration)
        cmd = "stress-ng --timeout " + str(random_input) +  " -c 0 -l " + str(workload_cpu_avg) + " ; " +\
                "stress-ng --timeout " + str(peak_duration) + " -c 0 -l " + str(workload_cpu_per) + " ; " +\
                "stress-ng --timeout " + str(slice_duration-random_input-peak_duration) +  " -c 0 -l " + str(workload_cpu_avg) + " ; "
        return cmd

    def generate_workload(self, slice_duration : int, workload_cpu_avg : int):
        return "stress-ng --timeout " + str(slice_duration) +  " -c 0 -l " + str(workload_cpu_avg) + " ; "

class VmSliceWorkloadWordpress(VmSliceWorkload):

    def generate_workload(self, slice_duration : int, workload_cpu_avg : int):
        return "siege.sh [TODO] " + str(workload_cpu_avg) + " ; "