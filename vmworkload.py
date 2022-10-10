from enum import Enum
import scipy.optimize
import numpy as np
import getopt, sys

class VmWorkload(Enum):
    LOW = 0
    MEDIUM_LOW = 0
    MEDIUM_HIGH = 0
    HIGH = 0

vm_workload_details = dict()
vm_workload_details[VmWorkload.LOW] =  {"avg": "[0;0.03]", "per" : "[0;0.25]"  }
vm_workload_details[VmWorkload.MEDIUM_LOW] =  {"avg": "]0.03;0.12]", "per" : "[0.25;0.60]"  }
vm_workload_details[VmWorkload.MEDIUM_HIGH] =  {"avg": "]0.12;0.25]", "per" : "[0.60;0.90]"  }
vm_workload_details[VmWorkload.HIGH] =  {"avg": "]0.25;0.90]", "per" : "[0.90;100]"  }

class Vm(object):

    vmcount = 0
    diurnal_workload = ["diurnalworkload.qcow2"]
    nodiurnal_workload = ["batchworkload.qcow2"]

    def __init__(self, cpu : int, mem : int, workload_intensity : VmWorkload, diurnal : bool):
        Vm.vmcount+=1
        self.vm_name="vm" + str(Vm.vmcount)
        self.cpu=cpu
        self.mem=mem
        self.workload_intensity=workload_intensity
        if diurnal:
            self.workload = Vm.diurnal_workload[0]
        else:
            self.workload = Vm.nodiurnal_workload[0]

    def generate_setup_command(self):
        return "./setup-vm.sh " + self.vm_name + " " + str(self.cpu) + " " + str(round(self.mem*1024)) + " " + self.workload

    def generate_workload_command(self):
        return "./setup-vm.sh " + self.vm_name + " " + str(self.cpu) + " " + str(round(self.mem*1024)) + " " + self.workload

######################
## Cpu Distribution ##
######################
def build_cpu_distribution(cpu : int):
    bnds = [(1, cpu) for i in range(4)]
    xinit = [1 for i in range(4)]
    fun = lambda x: (cpu_config - x[0]*1 + x[1]*2 + x[2]*4 + x[3]*8) # On minimise les coeurs non utilisées
    # ineq : Forces value to be greater than zero. 
    cons = [{'type': 'ineq', 'fun': lambda x:  x[0]*1 + x[1]*2 + x[2]*4 + x[3]*8 - cpu_config}, # Les coeurs alloués ne peuvent dépasser 256
            {'type': 'ineq', 'fun': lambda x:  x[0]/(np.sum(x)) - 0.6}, # 60% de VM de type 1
            {'type': 'ineq', 'fun': lambda x:  x[1]/(np.sum(x)) - 0.2}, # 20% de VM de type 2
            {'type': 'ineq', 'fun': lambda x:  x[2]/(np.sum(x)) - 0.2}, # 20% de VM de type 3
            {'type': 'ineq', 'fun': lambda x:  x[3]/(np.sum(x)) - 0.1}] # 10% de VM de type 4
    results = scipy.optimize.minimize(fun, x0=xinit, bounds=bnds, constraints=cons, method='SLSQP') # options={'disp': True}
    keys = [1,2,4,8]
    count = 0
    totalvm = 0
    totalvcpu = 0
    vmconfiglist=list()
    for val in results['x']:
        #print("vcpu", keys[count], round(val))
        vmconfiglist+= [(keys[count], -1) for j in range(round(val))]
        totalvm+=round(val)
        totalvcpu+= round(val)*keys[count]
        count+=1
    return totalvm, totalvcpu, vmconfiglist

######################
## Mem Distribution ##
######################
def build_mem_distribution(totalvm : int, vmconfiglist : list):
    init_mem_count=[(round(0.05*totalvm), 0.75), (round(0.45*totalvm), 1.75), (round(0.2*totalvm), 3.5), (round(0.15*totalvm), 7), (round(1*totalvm), 14)]
    init_mem_current_count=0
    init_mem_index=0
    total_mem=0
    for i in range(totalvm):
        current_max_count, current_alloc = init_mem_count[init_mem_index]
        vmconfiglist[i] = (vmconfiglist[i][0], current_alloc) # Update config list with memory intel
        total_mem+=current_alloc
        init_mem_current_count+=1
        if(init_mem_current_count>=current_max_count):
            init_mem_index+=1
            init_mem_current_count=0
    return total_mem, vmconfiglist

########################
## Usage distribution ##
########################
diurnal_pattern=0.3
def add_vms(current_list : list, vm_config_tuple : tuple, count : int, workload_intensity : VmWorkload, number_of_diurnal : int):
    diurnal_count = 0
    for x in range (count):
        if diurnal_count < number_of_diurnal:
            diurnal=True
            diurnal_count+=1
        else:
            diurnal=False
        current_list.append(Vm(cpu=vm_config_tuple[0], mem=vm_config_tuple[1],
                                workload_intensity=workload_intensity,
                                diurnal=diurnal
                                )
                            )

def compute_usage(vmlist : list, vm_config_tuple : tuple, count : int):
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
    add_vms(current_list=vmlist, vm_config_tuple=vm_config_tuple, count=first_slice, workload_intensity=VmWorkload.LOW, number_of_diurnal=round(first_slice*diurnal_pattern))
    add_vms(current_list=vmlist, vm_config_tuple=vm_config_tuple, count=second_slice, workload_intensity=VmWorkload.MEDIUM_LOW, number_of_diurnal=round(second_slice*diurnal_pattern))
    add_vms(current_list=vmlist, vm_config_tuple=vm_config_tuple, count=third_slice, workload_intensity=VmWorkload.MEDIUM_HIGH, number_of_diurnal=round(third_slice*diurnal_pattern))
    add_vms(current_list=vmlist, vm_config_tuple=vm_config_tuple, count=fourth_slice, workload_intensity=VmWorkload.HIGH, number_of_diurnal=round(fourth_slice*diurnal_pattern))
    return "\n  >" + str(first_slice) + " avg/per" + vm_workload_details[VmWorkload.LOW]["avg"] + "/" + vm_workload_details[VmWorkload.LOW]["per"]  + " avec " + str(round(first_slice*diurnal_pattern)) + " diurnal" +\
         "\n  >" + str(second_slice) + " avg/per" + vm_workload_details[VmWorkload.MEDIUM_LOW]["avg"] + "/" + vm_workload_details[VmWorkload.MEDIUM_LOW]["per"] + " avec " + str(round(second_slice*diurnal_pattern)) + " diurnal" +\
         "\n  >" + str(third_slice) + " avg/per" + vm_workload_details[VmWorkload.MEDIUM_HIGH]["avg"] + "/" + vm_workload_details[VmWorkload.MEDIUM_HIGH]["per"] + " avec " + str(round(third_slice*diurnal_pattern)) + " diurnal" +\
         "\n  >" + str(fourth_slice) + " avg/per" + vm_workload_details[VmWorkload.HIGH]["avg"] + "/" + vm_workload_details[VmWorkload.HIGH]["per"] + " avec " + str(round(fourth_slice*diurnal_pattern)) + " diurnal"

def build_usage_distribution(totalvm : int, vmconfiglist : list):
    count=0
    before=vmconfiglist[0]
    vmlist=list()
    print("Type of VM")
    for i in range(totalvm):
        if before != vmconfiglist[i]:
            print(str(before[0]) + "c-" + str(before[1]) + "gb", ":", count, "vm dont", compute_usage(vmlist, before, count))
            count=0
        count+=1
        before=vmconfiglist[i]
    print(str(before[0]) + "c-" + str(before[1]) + "gb", ":", count, "vm dont", compute_usage(vmlist, before, count))
    return vmlist

########################
####  Distribution  ####
########################
def build_distribution(cpu : int, mem : int):
    totalvm, totalvcpu, vmconfiglist = build_cpu_distribution(cpu=cpu)
    totalmem, vmconfiglist = build_mem_distribution(totalvm=totalvm, vmconfiglist=vmconfiglist)
    vm_list = build_usage_distribution(totalvm=totalvm, vmconfiglist=vmconfiglist)
    print("")
    print("Total VM", totalvm)
    print("Total vcpu", totalvcpu, "/", cpu_config)
    print("Total mem", totalmem, "/", mem_config)
    return vm_list

if __name__ == '__main__':

    short_options = "hswc:m:"
    long_options = ["help","setup-cmd", "workload-cmd", "cpu=","mem="]
    debug = 0
    
    cpu_config = 256*2
    mem_config = 1000
    generate_setup_command=False
    generate_workload_command=False

    try:
        arguments, values = getopt.getopt(sys.argv[1:], short_options, long_options)
    except getopt.error as err:
        print (str(err)) # Output error, and return with an error code
        sys.exit(2)
    for current_argument, current_value in arguments:
        if current_argument in ("-c", "--cpu"):
            cpu_config = int(current_value)
        elif current_argument in ("-m", "--mem"):
            mem_config = int(current_value)
        elif current_argument in ("-s", "--setup-cmd"):
            generate_setup_command=True
        elif current_argument in ("-w", "--workload-cmd"):
            generate_workload_command=True
        else:
            print("python3 vmworkload.py [--help] [--cpu={cores}] [--mem={mo}] [--setup-cmd] [--workload-cmd]")
            sys.exit(0)

    try:
        vm_list = build_distribution(cpu=cpu_config, mem=mem_config)
        if generate_setup_command:
            for x in vm_list:
                print(x.generate_setup_command())
        if generate_workload_command:
            for x in vm_list:
                print(x.generate_workload_command())
    except KeyboardInterrupt:
        print("Program interrupted")
