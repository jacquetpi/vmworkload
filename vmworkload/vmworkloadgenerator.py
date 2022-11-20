import random
import numpy as np
from vmworkload.vmmodel import VmModel, VmWorkloadType

class VmWorkloadGenerator(object):

    def __init__(self, slice_duration : int, scope_duration : int, number_of_scope : int, vm_workload_details: dict):
        self.slice_duration=slice_duration
        self.scope_duration=scope_duration

        self.number_of_slices_per_scope=int(scope_duration/slice_duration)
        self.number_of_scope=number_of_scope

        self.vm_workload_details=vm_workload_details

    def __get_vm_identifier(self, vm : VmModel, remote : bool):
        if remote:
            return "${remoteip}:" + str(vm.get_host_port())
        else:
            return vm.get_name()

    def __generate_avg_and_percentile(self, vm : VmModel):
        workload = self.vm_workload_details[getattr(vm, "workload_intensity")]
        workload_cpu_avg = random.randrange(workload["avg"][0], workload["avg"][1])
        workload_cpu_per = random.randrange(workload["per"][0], workload["per"][1])
        #print("cpu", workload_cpu_avg, "nth", workload_cpu_per)
        return workload_cpu_avg, workload_cpu_per

    def __generate_gaussian_distribution_from_model(self, vm : VmModel):
        workload_cpu_avg, workload_cpu_per = self.__generate_avg_and_percentile(vm)
        return self.__generate_gaussian_distribution_from_avg(workload_cpu_avg, workload_cpu_per)

    def __generate_gaussian_distribution_from_avg(self, workload_avg : int, workload_95th : int):
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

    def __get_random_value_in(self, distribution_values):
        return round(distribution_values[random.randrange(len(distribution_values))])

    def __distribute_to_slice(self, vm : VmModel, workload_cpu, remote : bool = False):
        return VmModel.generator[getattr(vm, "workload")].generate_workload(
            vm_identifier=self.__get_vm_identifier(vm=vm, remote=remote),
            slice_duration=self.slice_duration, 
            workload_cpu_avg=workload_cpu)

    def __generate_periodic_workload(self, vm : VmModel, remote : bool = False):
        gaussian = self.__generate_gaussian_distribution_from_model(vm=vm)
        value_per_slice = list()
        for j in range(self.number_of_slices_per_scope):
            value_per_slice.append(self.__get_random_value_in(gaussian))
            
        cmd_generated = ""
        for i in range(self.number_of_scope):
            for j in range(self.number_of_slices_per_scope):
                cmd_generated += self.__distribute_to_slice(vm, value_per_slice[j],remote=remote)    
        return cmd_generated

    def __generate_nonperiodic_workload(self, vm : VmModel, remote : bool = False):
        gaussian = self.__generate_gaussian_distribution_from_model(vm=vm)
        cmd_generated = ""
        for i in range(self.number_of_scope):
            for j in range(self.number_of_slices_per_scope):
                cmd_generated += self.__distribute_to_slice(vm, self.__get_random_value_in(gaussian), remote=remote)
        return cmd_generated
            
    def generate_workload_for_VM(self, vm : VmModel, remote : bool = False):
        if(getattr(vm, "periodic")):
            return self.__generate_periodic_workload(vm=vm, remote=remote)
        else:
            return self.__generate_nonperiodic_workload(vm=vm, remote=remote)