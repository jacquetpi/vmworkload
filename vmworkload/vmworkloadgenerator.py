import random
import numpy as np
from vmworkload.vmmodel import VmModel, VmWorkloadType

class VmWorkloadGenerator(object):

    def __init__(self, slice_duration : int, scope_duration : int, number_of_scope : int, vm_workload_details: dict):
        self.slice_duration=slice_duration
        self.scope_duration=scope_duration
        self.number_of_scope=number_of_scope
        self.vm_workload_details=vm_workload_details

    def generate_distribution(self, workload_avg, workload_95th):
        mu, sigma = workload_avg, workload_95th
        while True:
            #print(mu, sigma)
            s = np.random.normal(mu, sigma, 1000)
            x = [abs(item) for item in s]
            if (np.percentile(x,95)<=workload_95th):
                break
            sigma-=1
            if(sigma<=1):
                s = np.random.normal(mu, sigma, 100)
                break
        return x
        # count, bins, ignored = plt.hist(x, 10, density=True)
        # plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (bins - mu)**2 / (2 * sigma**2) ), linewidth=2, color='r')
        # plt.show()import numpy as np

    def generate_workload_diurnal(self):
        print("todo")

    def generate_workload_for_VM(self, vm : VmModel):
        workload = self.vm_workload_details[getattr(vm, "workload_intensity")]
        workload_cpu_avg = random.randrange(workload["avg"][0], workload["avg"][1])
        workload_cpu_per = random.randrange(workload["per"][0], workload["per"][1])
        print("cpu", workload_cpu_avg, "nth", workload_cpu_per)
        if(getattr(vm, "diurnal")):
            self.generate_workload_diurnal()

        # print("")
        # occurences_of_slice : list()
        # pitch = 100/TEMP_number_of_scope
        # for i in range(0,TEMP_number_of_scope):
        #     print("Debug", x[random.randrange(len(x))])

        # cmd = {
        #     'idle': self.generate_workload_idle(scope_duration=scope_duration, slice_duration=slice_duration, workload_cpu_avg=workload_cpu_avg, workload_cpu_per=workload_cpu_per),
        #     'stressng': self.generate_workload_stressng(scope_duration=scope_duration, slice_duration=slice_duration, workload_cpu_avg=workload_cpu_avg, workload_cpu_per=workload_cpu_per),
        # }[self.workload]
        # return self.sshheader.replace("{data}", cmd)