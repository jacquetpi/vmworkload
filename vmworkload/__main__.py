import getopt, sys, json
from vmworkload.vmmodel import *
from vmworkload.nodegenerator import NodeGenerator
from vmworkload.vmworkloadgenerator import VmWorkloadGenerator

if __name__ == '__main__':

    short_options = "hsw:c:m:l:"
    long_options = ["help","setup-cmd", "workload-cmd=", "cpu=", "mem=", "load="]
    debug = 0
    
    cpu_config = 256*2
    mem_config = 1000
    generate_setup_command=False
    generate_workload_command=False
    generate_workload_slice=0
    loaded_config=False

    try:
        arguments, values = getopt.getopt(sys.argv[1:], short_options, long_options)
    except getopt.error as err:
        print(str(err))
        sys.exit(2)
    usage = "python3 -m vmworkload [--help] [--cpu={cores}] [--mem={mo}] [--setup-cmd] [--load=] [--workload-cmd={slice,scope,iteration}]"
    for current_argument, current_value in arguments:
        if current_argument in ("-c", "--cpu"):
            cpu_config = int(current_value)
        elif current_argument in ("-m", "--mem"):
            mem_config = int(current_value)
        elif current_argument in ("-s", "--setup-cmd"):
            generate_setup_command=True
        elif current_argument in ("-w", "--workload-cmd"):
            generate_workload_command=True
            args = current_value.split(',')
            generate_workload_slice = int(args[0])
            generate_workload_scope = int(args[1])
            generate_workload_iteration = int(args[2])
            if generate_workload_slice > generate_workload_scope:
                print(usage)
                raise ValueError("Model scope must be greater than slice scope")
            if generate_workload_scope % generate_workload_slice !=0:
                print(usage)
                raise ValueError("Model scope must be a slice multiple")
        elif current_argument in ("-l", "--load"):
            with open(current_value, 'r') as f:
                loaded_config=True
                raw_list = json.load(f)
                vm_list = list()
                for raw_vm in raw_list:
                    vm_list.append(VmModel(cpu=raw_vm["cpu"], mem=raw_vm["mem"],
                                    workload_intensity=raw_vm["workload_intensity"],
                                    periodic=raw_vm["periodic"], vm_name=raw_vm["vm_name"], workload=raw_vm["workload"]
                                    )
                                )
        else:
            print(usage)
            sys.exit(0)

    try:
        node_generator = NodeGenerator()
        if not loaded_config:
            vm_list = node_generator.generate_node(cpu=cpu_config, mem=mem_config)
        if generate_setup_command:
            i=0
            with open('setup.sh', 'w') as f:
                for x in vm_list:
                    f.write("( " + x.get_setup_command() + " ) &")
                    f.write('\n')
                    i+=1
                    if (i%10==0):
                        f.write('sleep 1200\n')
            with open("node-specifications.json", 'w') as f:
                f.write(json.dumps(vm_list, cls=VmModelEncoder))
            print("Setup wrote in setup.sh and specification in node-specifications.json")
        if generate_workload_command:
            vmworkload_generator = VmWorkloadGenerator(slice_duration=generate_workload_slice, scope_duration=generate_workload_scope, number_of_scope=generate_workload_iteration, vm_workload_details=node_generator.get_workload_details())
            with open('workload.sh', 'w') as f:
                for x in vm_list:
                    f.write("( " + vmworkload_generator.generate_workload_for_VM(x) + " ) &")
                    f.write('\n')
            print("Workload wrote in workload.sh")
    except KeyboardInterrupt:
        print("Program interrupted")
