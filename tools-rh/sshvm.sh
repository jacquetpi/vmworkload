#!/bin/bash
vm_ip=$( virsh --connect=qemu:///system domifaddr "$1" | tail -n 2 | head -n 1 | awk '{ print $4 }' | sed 's/[/].*//' );
ssh vmtornado@"${vm_ip}" -o StrictHostKeyChecking=no "$2"