import random

class VmSliceWorkload(object):

    def generate_slice(self):
        return "Not implemented"

class VmSliceWorkloadIdle(VmSliceWorkload):

    def generate_slice(self, scope_duration : int, slice_duration : int, workload_cpu_avg : int, workload_cpu_per : int):
        cmd = ""
        number_of_slice = int(scope_duration/slice_duration)
        peak_duration = 10
        random_input = random.randrange(0,scope_duration-peak_duration)
        for x in range(number_of_slice):
            cmd+= "sleep " + str(random_input) +  " ; " +\
                "stress-ng --timeout " + str(peak_duration) + " -c 0 -l " + str(workload_cpu_per) + " ; " +\
                "sleep " + str(scope_duration-random_input-peak_duration) + " ; "
        return cmd

class VmSliceWorkloadStressNG(VmSliceWorkload):

    def generate_workload_stressng__of_slice_with_peak(self, slice_duration : int, workload_cpu_avg : int, workload_cpu_per : int, random_input : int = 0, peak_duration : int = 10):
        if random_input <=0:
            random_input = random.randrange(0,slice_duration-peak_duration)
        slice_cmd = "stress-ng --timeout " + str(random_input) +  " -c 0 -l " + str(workload_cpu_avg) + " ; " +\
                "stress-ng --timeout " + str(peak_duration) + " -c 0 -l " + str(workload_cpu_per) + " ; " +\
                "stress-ng --timeout " + str(slice_duration-random_input-peak_duration) +  " -c 0 -l " + str(workload_cpu_avg) + " ; "
        return random_input, slice_cmd

    def generate_workload_stressng(self, scope_duration : int, slice_duration : int, workload_cpu_avg : int, workload_cpu_per : int):
        number_of_slice = int(scope_duration/slice_duration)
        cmd=""
        random_input=0
        if self.diurnal:
            odd_test = number_of_slice % 2
            for x in range(int(number_of_slice/2)):
                random_input, slice_cmd = self.generate_workload_stressng__of_slice_with_peak(slice_duration=slice_duration, workload_cpu_avg=workload_cpu_avg, workload_cpu_per=workload_cpu_per, random_input=random_input)
                cmd+=slice_cmd
                random_input, slice_cmd = self.generate_workload_stressng__of_slice_with_peak(slice_duration=slice_duration, workload_cpu_avg=workload_cpu_avg, workload_cpu_per=workload_cpu_per, random_input=random_input)
                cmd+=slice_cmd
            if odd_test>0:
                random_input, slice_cmd = self.generate_workload_stressng__of_slice_with_peak(slice_duration=slice_duration, workload_cpu_avg=workload_cpu_avg, workload_cpu_per=workload_cpu_per, random_input=random_input)
                cmd+=slice_cmd
        else:
            for x in range(number_of_slice):
                random_input, slice_cmd = self.generate_workload_stressng__of_slice_with_peak(slice_duration=slice_duration, workload_cpu_avg=workload_cpu_avg, workload_cpu_per=workload_cpu_per, random_input=random_input)
                cmd+=slice_cmd
        return cmd