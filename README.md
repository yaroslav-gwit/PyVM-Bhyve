# Welcome to the PyVM Bhyve community!
 > WARNING! Software is in alpha release state. Use at your own risk and don't blame me if something breaks :) This is my first Python project, and there are a lot of hardcoded values, mainly Python dev environment and system paths. Keep these default for now, I'll clean up everything eventually.

This project was born out of necessity for fast VM deployments on a "not so modern" hardware, be it an old Dell Optiplex PC or a used Lenovo Thinkpad -- you don't always have the means to buy all new and powerful. On one hand, you have old and/or cheap hardware, on the other one, there is modern and mighty hardware -- PyVM works very well with both.

With help of FreeBSD, ZFS, Bhyve, Cloud-Init, and a bit of Python I was able to achieve impressive results: VM is deployed from start to finish (including SSH keys, IP address, hostname, etc) within 3-4 seconds or less depending on the hardware.

I personally use PyVM Bhyve on all of my hosting nodes for its portability, reliability, and deployment speed (it's a FreeBSD system after all :rocket:).

# Software installation
1. Install FreeBSD, use ZFS as a file system (leave zroot as a pool name), enable Unbound as your local DNS resolver.
2. Install required software:
```
pkg update
pkg install git nano python3 
# Install this as well, if you'd be deploying PyVM from the same machine:
pkg install py38-ansible
```
3. Clone the repo and create inventory file for ansible to use:
```
mkdir /root/pyVM/ && git clone https://github.com/yaroslav-gwit/PyVM-Bhyve.git /root/pyVM/
cp /root/pyVM/ansible_deployment_scripts/example_inventory_pyvm.yml /root/pyVM/ansible_deployment_scripts/inventory_pyvm.yml
```
4. Adjust values in the inventory file, and run the Ansible playbook to install PyVM Bhyve.
```
cd /root/pyVM/ansible_deployment_scripts/
ansible-playbook playbook_pyvm.yml
```
 > NOTE! This type of installtion is not recommended, but can give you an idea of what PyVM is, and if it is something you are intererted in.

### Production deployment would look something like this:
#### 1. Prepare a machine that will control your fleet of nodes.
This will be an Ansible "controller" machine. It might be your personal laptop, or a VM somewhere remote, just keep in mind: it will hold all of your ZFS encryption keys. If you lose it - game over, your data is gone.
#### 2. Encrypt inventory file.
This is self explanatory - use Ansible Vault to keep your inventory file safe, because it has all of your encryption keys in it.
#### 3. Distribute your SSH keys and start deploying!
Once inventory file is in order, you can start deploying PyVM Bhyve to a large fleet of machines.

# Documentation
Would like to try out PyVM? Check out the docs: https://github.com/yaroslav-gwit/PyVM-Bhyve/wiki

# Roadmap
 > Please keep in mind that this roadmap is not ordered. I'll be dealing with each item on this list when I have the time and/or in the mood to do so :)

 - Simplify Windows type image deployments: create a script that reads IP address and hostname values from the text file (cloud-init config file preferably) and applies these values to the system.
 - Finish up the preparation of all OS images.
 - Switch from argparse to Typer: will make a help output cleaner, autocomplete for fish, and easier to read/maintain source code.
 - Get all custom/manual flags in order: IP address, MAC address, Network Bridge, etc.
 - Add more "try" methods for core functions to send a correct error to the user.
 - Make a logo for the project.
 - Use colorama to provide better insights from the table output.
 - Rewrite string concatenations to use Format module. This will improve project development speed and maintenability.
 - Describe the usecases and target audience.
 - Include some diagrams to make the documentation look more attractive.
 - Add more images to the supported OS list (Devuan, Arch Linux, Alpine Linux, OpenBSD, etc would be great to have too, but it's just too much work to support all these OSes on my own at the moment).
 - Complete the documentation.
 - Decouple VM image download and deployment code from the VM_DEPLOY class, to allow user defined VM images and/or custom OS types.
 - Review the project on my YT channel, to bring more awareness.
 - Document Nebula integration, to support deployments at a large scale.
 - Rewrite the hardcoded values (to be more flexible with ZFS pools/datasets, VM image locations, etc).
 - Gather community feedback.
 - Add support for a Global DNS, using NSD DNS server from NLnet Labs (creator of Unbound).
 - Create an API, to be able to use this project at scale (based on FastAPI).
 - Create a simple web dashboard based on React, to display number and status of hosts/VMs, system health, etc.
 - Create a man-like and PDF documentation, for the offline use.
 - ZFS pull-type replication implementation (only push-type is ready at the moment).
 - "Distributed" backup types: spread VMs across the pool of nodes for better data protection. At the moment only simple type backups are supported - VMs from multiple nodes are replicated to one (or few) backup server(s).
 - High availability options for the VMs or hoster nodes (something similar to CARP failover with OPNSense/pfSense).
 - "Hot" spare backup node automatic takeover in case if one of the production nodes is down.
 - Read the book about PF, and keep up with the best practices.
 - Better PF integration: add a flag to `pyvm` to allow traffic between a group of VMs.
 - Add ACLs or gather VMs into groups (by user, group) etc. Suggestions are welcome, but the idea here is to allow certain VMs to talk to one another if they are in the same group: this will lay a great foundation for a quick deployment of isolated clusters - Kubernetes, GlusterFS, Docker Swarm, etc.
 - FreeBSD tuning and ZFS tuning.
 - Intergration with HAProxy Manager, to provide an easy way to proxy HTTP/TCP traffic to the backend VMs.
 - Develop a support package offering for the "bigger players". This will allow me to dedicate more time for this project.

### Nice to have (but not a priority)
 - TUI for the console: it's nice to be able to navigate a terminal interface using arrows and enter/space keys, so you don't have to remember all of the commands that are involved in the process.
 - Fully featured WebUI written in React/Vue
 - Custom FreeBSD installation image to make it easier to start with a project.

# Would like to donate to directly support project development?
You can throw few dollars at me here:
https://www.buymeacoffee.com/yaroslavkoisa
