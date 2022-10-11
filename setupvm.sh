#!/bin/bash
if (( "$#" != "3" )) 
then
  echo "Missing argument : ./setupvm.sh name core mem"
  exit -1
fi
sudo rm /var/lib/libvirt/images/"$1".qcow2
virsh --connect=qemu:///system destroy "$1"
virsh --connect=qemu:///system undefine "$1"
sudo cp /var/lib/libvirt/images/baseline-ubuntu20-04.qcow2 /var/lib/libvirt/images/"$1".qcow2
virt-install --connect qemu:///system --import --name "$1" --vcpu "$2" --memory "$3" --disk /var/lib/libvirt/images/"$1".qcow2,format=qcow2,bus=virtio --import --os-variant ubuntu20.04 --network default --virt-type kvm --noautoconsole --check path_in_use=off
# Setup statistics
virsh --connect qemu:///system dommemstat "$1" --period 1
# Setup core pining
for ((vcpu=0;vcpu<"$2";vcpu++)); do
    virsh --connect=qemu:///system vcpupin "$1" --vcpu "${vcpu}" 1-3
done
virsh --connect=qemu:///system vcpupin "$1"
# Start
virsh --connect=qemu:///system start "$1"
sleep 10
virsh --connect=qemu:///system domifaddr "$1"
