from random import randrange
from enum import Enum

class VmWorkloadType(Enum):
    LOW = 0
    MEDIUM_LOW = 1
    MEDIUM_HIGH = 2
    HIGH = 3

class VmModel(object):

    vmcount = 0
    diurnal_workload = ["stressng","wordpress"]
    nodiurnal_workload = ["idle"] + diurnal_workload

    def __init__(self, cpu : int, mem : int, workload_intensity : VmWorkloadType, diurnal : bool):
        VmModel.vmcount+=1
        self.vm_name="vm" + str(VmModel.vmcount)
        self.sshheader = "vmssh " + self.vm_name + " -o StrictHostKeyChecking=no \"{data}\""
        self.cpu=cpu
        self.mem=mem
        self.workload_intensity=workload_intensity
        self.diurnal=diurnal
        if diurnal:
            self.workload = VmModel.diurnal_workload[randrange(len(VmModel.diurnal_workload))]
        else:
            if workload_intensity == VmWorkloadType.LOW:
                self.workload = VmModel.nodiurnal_workload[0]
            else:
                self.workload = VmModel.nodiurnal_workload[randrange(1,len(VmModel.nodiurnal_workload))]

    def get_setup_command(self):
        if self.workload == "stressng" or self.workload == "idle":
            return "./setupvm.sh " + self.vm_name + " " + str(self.cpu) + " " + str(round(self.mem*1024)) + " " + self.workload
        else:
            return "./setupvm.sh " + self.vm_name + " " + str(self.cpu) + " " + str(round(self.mem*1024)) + " " + self.workload
