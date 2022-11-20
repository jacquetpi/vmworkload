from random import randrange
from enum import Enum
from .vmsliceworkload import *
import json
from json import JSONEncoder

class VmWorkloadType(str, Enum):
    LOW = 0
    MEDIUM_LOW = 1
    MEDIUM_HIGH = 2
    HIGH = 3

class VmModel(object):

    TOOL_FOLDER = "tools/"

    vmcount = 0
    periodic_workload = ["dsb", "wordpress", "stressng", "tpcc"]
    notperiodic_workload = periodic_workload + ["idle"]
    generator = {"idle" : VmSliceWorkloadIdle(), 
            "stressng" : VmSliceWorkloadStressNG(),
            "wordpress" : VmSliceWorkloadWordpress(),
            "dsb" : VmSliceWorkloadDeathStarBench(),
            "tpcc" : VmSliceWorkloadTpcc(),
            "tpch" : VmSliceWorkloadTpch()}

    def __init__(self, cpu : int, mem : int, workload_intensity : VmWorkloadType, periodic : bool, workload = None, vm_name=None):
        VmModel.vmcount+=1
        if vm_name==None:
            self.vm_name="vm" + str(VmModel.vmcount)
        else:
            self.vm_name=vm_name
        self.host_port = 11000 + VmModel.vmcount # if required for remote workload
        self.cpu=cpu
        self.mem=mem
        self.workload_intensity=workload_intensity
        self.periodic=periodic
        if workload!=None:
            self.workload=workload
            return
        if self.mem < 7: # GB : dsb needs more memory so we exclude it from range
            workload_range_index=1
        else:
            workload_range_index=0
        # Choose workload randomly
        if self.periodic:
            self.workload = VmModel.periodic_workload[randrange(workload_range_index, len(VmModel.periodic_workload))]
            self.vm_name+= "periodic"
        else:
            self.vm_name+= "notperiodic"
            if workload_intensity == VmWorkloadType.LOW:
                self.workload = VmModel.notperiodic_workload[-1] # idle
            else:
                self.workload = VmModel.notperiodic_workload[randrange(workload_range_index, len(VmModel.notperiodic_workload)-1)]

    def get_setup_command(self):
        return VmModel.TOOL_FOLDER + "setupvm.sh " + self.vm_name + " " + str(self.cpu) + " " + str(round(self.mem*1024)) + " " + self.workload

    def get_nat_setup_command(self):
        return VmModel.TOOL_FOLDER + "setupvmnat.sh " + self.vm_name + " " + self.workload + " " + str(self.host_port)

    def get_name(self):
        return self.vm_name

    def get_host_port(self):
        return self.host_port
        
class VmModelEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__  