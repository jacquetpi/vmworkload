from random import randrange
from enum import Enum
from .vmsliceworkload import *

class VmWorkloadType(Enum):
    LOW = 0
    MEDIUM_LOW = 1
    MEDIUM_HIGH = 2
    HIGH = 3

class VmModel(object):

    TOOL_FOLDER = "/usr/local/src/vmworkload/tools/"

    vmcount = 0
    periodic_workload = ["stressng", "wordpress", "dsb", "tpcc"]
    notperiodic_workload = ["idle"] + periodic_workload
    generator = {"idle" : VmSliceWorkloadIdle(), 
            "stressng" : VmSliceWorkloadStressNG(),
            "wordpress" : VmSliceWorkloadWordpress(),
            "dsb" : VmSliceWorkloadDeathStarBench(),
            "tpcc" : VmSliceWorkloadTpcc(),
            "tpch" : VmSliceWorkloadTpch()}

    def __init__(self, cpu : int, mem : int, workload_intensity : VmWorkloadType, periodic : bool):
        VmModel.vmcount+=1
        self.vm_name="vm" + str(VmModel.vmcount)
        self.cpu=cpu
        self.mem=mem
        self.workload_intensity=workload_intensity
        self.periodic=periodic
        if self.periodic:
            self.workload = VmModel.periodic_workload[randrange(len(VmModel.periodic_workload))]
            self.vm_name+= "-periodic"
        else:
            self.vm_name+= "-notperiodic"
            if workload_intensity == VmWorkloadType.LOW:
                self.workload = VmModel.notperiodic_workload[0]
            else:
                self.workload = VmModel.notperiodic_workload[randrange(1,len(VmModel.notperiodic_workload))]

    def get_setup_command(self):
        return VmModel.TOOL_FOLDER + "setupvm.sh " + self.vm_name + " " + str(self.cpu) + " " + str(round(self.mem*1024)) + " " + self.workload
