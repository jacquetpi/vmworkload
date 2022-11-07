import getopt, sys
from vmworkload.vmmodel import VmModel, VmWorkloadType
from vmworkload.nodegenerator import NodeGenerator
from vmworkload.vmworkloadgenerator import VmWorkloadGenerator

if __name__ == '__main__':

    short_options = "hsw:c:m:"
    long_options = ["help","setup-cmd", "workload-cmd=", "cpu=","mem="]
    debug = 0
    
    cpu_config = 256*2
    mem_config = 1000
    generate_setup_command=False
    generate_workload_command=False
    generate_workload_slice=0

    try:
        arguments, values = getopt.getopt(sys.argv[1:], short_options, long_options)
    except getopt.error as err:
        print(str(err))
        sys.exit(2)
    usage = "python3 -m vmworkload [--help] [--cpu={cores}] [--mem={mo}] [--setup-cmd] [--workload-cmd={slice,scope,iteration}]"
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
        else:
            print(usage)
            sys.exit(0)

    try:
        node_generator = NodeGenerator()
        vm_list = node_generator.generate_node(cpu=cpu_config, mem=mem_config)
        if generate_setup_command:
            i=0
            with open('setup.sh', 'w') as f:
                for x in vm_list:
                    f.write("( " + x.get_setup_command() + " ) &")
                    f.write('\n')
                    i+=1
                    if (i%10==0):
                        f.write('sleep 900\n')
            print("Setup wrote in setup.sh")
        if generate_workload_command:
            vmworkload_generator = VmWorkloadGenerator(slice_duration=generate_workload_slice, scope_duration=generate_workload_scope, number_of_scope=generate_workload_iteration, vm_workload_details=node_generator.get_workload_details())
            with open('workload.sh', 'w') as f:
                for x in vm_list:
                    f.write("( " + vmworkload_generator.generate_workload_for_VM(x) + " ) &")
                    f.write('\n')
            # vmworkload_generator.generate_workload_for_VM(vm_list[0])
            # vmworkload_generator.generate_workload_for_VM(vm_list[-1])
            print("Workload wrote in workload.sh")
    except KeyboardInterrupt:
        print("Program interrupted")
