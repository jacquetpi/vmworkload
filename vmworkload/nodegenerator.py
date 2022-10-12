import scipy.optimize
import numpy as np
from vmworkload.vmmodel import VmModel, VmWorkloadType

class NodeGenerator(object):

    def __init__(self):
        # Implements parameters issued from Azure dataset
        self.diurnal_pattern=0.3
        self.vm_workload_details = dict()
        self.vm_workload_details[VmWorkloadType.LOW] =  {"avg": (1,3), "per" : (3,25) } #per = 95th percentile
        self.vm_workload_details[VmWorkloadType.MEDIUM_LOW] =  {"avg": (3,12), "per" : (25,60)  }
        self.vm_workload_details[VmWorkloadType.MEDIUM_HIGH] =  {"avg": (12,25), "per" : (60,90)  }
        self.vm_workload_details[VmWorkloadType.HIGH] =  {"avg": (25,90), "per" : (90,100)  }
        self.vm_cpu_distribution = [0.6, 0.2, 0.2, 0.1] # Sum must be 1
        self.vm_cpu_config       = [1, 2, 4, 8] # In cores
        self.vm_mem_distribution = [0.05, 0.45, 0.2, 0.15, 1] # Sum should be 1 but we put last to 1 to handle rounded vm values
        self.vm_mem_config       = [0.75, 1.75, 3.5, 7, 14] # In GB


    def get_workload_details(self):
        return self.vm_workload_details

    def generate_node(self, cpu : int, mem : int):
        totalvm, totalvcpu, vmconfiglist = self.build_cpu_distribution(cpu=cpu)
        totalmem, vmconfiglist = self.build_mem_distribution(totalvm=totalvm, vmconfiglist=vmconfiglist)
        vm_list = self.build_usage_distribution(totalvm=totalvm, vmconfiglist=vmconfiglist)
        print("")
        print("Total VM", totalvm)
        print("Total vcpu", totalvcpu, "/", cpu)
        print("Total mem", totalmem, "/", mem)
        return vm_list

    ######################
    ## Cpu Distribution ##
    ######################
    def build_cpu_distribution(self, cpu : int):
        bnds = [(1, cpu) for i in range(4)]
        xinit = [1 for i in range(4)]
        # fun = lambda x: (cpu - np.sum(np.multiply(x,self.vm_cpu_config))) # We minimize the number of unused cpu...
        # cons = [{'type': 'ineq', 'fun': lambda x:  np.sum(np.multiply(x,self.vm_cpu_config)) - cpu}] # ...Without bypassing the cpu number | ineq : force value to be greater than 0
        # for index in range(len(self.vm_cpu_distribution)):
        #     cons.append({'type': 'ineq', 'fun': lambda x:  x[index]/(np.sum(x)) - self.vm_cpu_distribution[index]}) # Apply the desired distribution
        #     print("debug>", self.vm_cpu_distribution[index])

        fun = lambda x: (cpu - x[0]*1 + x[1]*2 + x[2]*4 + x[3]*8)
        cons = [{'type': 'ineq', 'fun': lambda x:  x[0]*1 + x[1]*2 + x[2]*4 + x[3]*8 - cpu},
                {'type': 'ineq', 'fun': lambda x:  x[0]/(np.sum(x)) - 0.6}, 
                {'type': 'ineq', 'fun': lambda x:  x[1]/(np.sum(x)) - 0.2},
                {'type': 'ineq', 'fun': lambda x:  x[2]/(np.sum(x)) - 0.2},
                {'type': 'ineq', 'fun': lambda x:  x[3]/(np.sum(x)) - 0.1}]
        
        results = scipy.optimize.minimize(fun, x0=xinit, bounds=bnds, constraints=cons, method='SLSQP') # options={'disp': True}
        count = 0
        totalvm = 0
        totalvcpu = 0
        vmconfiglist=list()
        for val in results['x']:
            #print("vcpu", keys[count], round(val))
            vmconfiglist+= [(self.vm_cpu_config[count], -1) for j in range(round(val))]
            totalvm+=round(val)
            totalvcpu+= round(val)*self.vm_cpu_config[count]
            count+=1
        return totalvm, totalvcpu, vmconfiglist

    ######################
    ## Mem Distribution ##
    ######################
    def build_mem_distribution(self, totalvm : int, vmconfiglist : list):
        mem_config_count_per_type=list()
        for index in range(len(self.vm_mem_distribution)):
            mem_config_count_per_type.append((round(self.vm_mem_distribution[index]*totalvm), self.vm_mem_config[index])) # append tuple (count_of_config, config)
        mem_config_current_count=0
        mem_index=0
        total_mem_amount=0
        for i in range(totalvm):
            mem_config_current_max_count, current_alloc = mem_config_count_per_type[mem_index]
            vmconfiglist[i] = (vmconfiglist[i][0], current_alloc) # Update config list with memory intel
            total_mem_amount+=current_alloc
            mem_config_current_count+=1
            if(mem_config_current_count>=mem_config_current_max_count):
                mem_index+=1
                mem_config_current_count=0
        return total_mem_amount, vmconfiglist

    ########################
    ## Usage distribution ##
    ########################
    def add_vms(self, current_list : list, vm_config_tuple : tuple, count : int, workload_intensity : VmWorkloadType, number_of_diurnal : int):
        diurnal_count = 0
        for x in range (count):
            if diurnal_count < number_of_diurnal:
                diurnal=True
                diurnal_count+=1
            else:
                diurnal=False
            current_list.append(VmModel(cpu=vm_config_tuple[0], mem=vm_config_tuple[1],
                                    workload_intensity=workload_intensity,
                                    diurnal=diurnal
                                    )
                                )

    def compute_usage(self, vmlist : list, vm_config_tuple : tuple, count : int):
        count_per_slice=int(count*0.25)
        to_dispath=count-(count_per_slice*4)
        if to_dispath>0:
            first_slice=count_per_slice+1
            to_dispath-=1
        else:
            first_slice=count_per_slice
        if to_dispath>0:
            second_slice=count_per_slice+1
            to_dispath-=1
        else:
            second_slice=count_per_slice
        if to_dispath>0:
            third_slice=count_per_slice+1
            to_dispath-=1
        else:
            third_slice=count_per_slice
        fourth_slice=count_per_slice
        self.add_vms(current_list=vmlist, vm_config_tuple=vm_config_tuple, count=first_slice, workload_intensity=VmWorkloadType.LOW, number_of_diurnal=round(first_slice*self.diurnal_pattern))
        self.add_vms(current_list=vmlist, vm_config_tuple=vm_config_tuple, count=second_slice, workload_intensity=VmWorkloadType.MEDIUM_LOW, number_of_diurnal=round(second_slice*self.diurnal_pattern))
        self.add_vms(current_list=vmlist, vm_config_tuple=vm_config_tuple, count=third_slice, workload_intensity=VmWorkloadType.MEDIUM_HIGH, number_of_diurnal=round(third_slice*self.diurnal_pattern))
        self.add_vms(current_list=vmlist, vm_config_tuple=vm_config_tuple, count=fourth_slice, workload_intensity=VmWorkloadType.HIGH, number_of_diurnal=round(fourth_slice*self.diurnal_pattern))
        return "\n  >" + str(first_slice) + " avg/per " + str(self.vm_workload_details[VmWorkloadType.LOW]["avg"]) + "/" + str(self.vm_workload_details[VmWorkloadType.LOW]["per"])  + " avec " + str(round(first_slice*self.diurnal_pattern)) + " diurnal" +\
            "\n  >" + str(second_slice) + " avg/per " + str(self.vm_workload_details[VmWorkloadType.MEDIUM_LOW]["avg"]) + "/" + str(self.vm_workload_details[VmWorkloadType.MEDIUM_LOW]["per"]) + " avec " + str(round(second_slice*self.diurnal_pattern)) + " diurnal" +\
            "\n  >" + str(third_slice) + " avg/per " + str(self.vm_workload_details[VmWorkloadType.MEDIUM_HIGH]["avg"]) + "/" + str(self.vm_workload_details[VmWorkloadType.MEDIUM_HIGH]["per"]) + " avec " + str(round(third_slice*self.diurnal_pattern)) + " diurnal" +\
            "\n  >" + str(fourth_slice) + " avg/per " + str(self.vm_workload_details[VmWorkloadType.HIGH]["avg"]) + "/" + str(self.vm_workload_details[VmWorkloadType.HIGH]["per"]) + " avec " + str(round(fourth_slice*self.diurnal_pattern)) + " diurnal"

    def build_usage_distribution(self, totalvm : int, vmconfiglist : list):
        count=0
        before=vmconfiglist[0]
        vmlist=list()
        print("Type of VM")
        for i in range(totalvm):
            if before != vmconfiglist[i]:
                print(str(before[0]) + "c-" + str(before[1]) + "gb", ":", count, "vm dont", self.compute_usage(vmlist, before, count))
                count=0
            count+=1
            before=vmconfiglist[i]
        print(str(before[0]) + "c-" + str(before[1]) + "gb", ":", count, "vm dont", self.compute_usage(vmlist, before, count))
        return vmlist