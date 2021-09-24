# Welcome to the PyVM Bhyve community!
 > WARNING! Software is in alpha release state. Use at your own risk and don't blame me if something breaks :)
 > This is my first project of such caliber and there are a lot of hardcoded values, mainly Python dev environment and system paths. Keep these default for now, I'll clean up everything eventually.

This project was born out of necessity for fast VM deployments on a "not so modern" hardware, be it an old Dell Optiplex PC or a used Lenovo Thinkpad -- you don't always have the means to buy all new and powerful. On one hand you have an old and/or cheap hardware, on the other one there is a modern and mighty hardware -- PyVM works very well with both.

With help of FreeBSD, ZFS, Bhyve, Cloud Init and a small bit of Python code I was able to achieve an impressive results: VM is deployed from start to finish (including SSH keys, IP address, hostname, etc) within 3-4 seconds or less depending on the hardware.

Today, project is in use by many for it's portability, reliability and speed (it's a FreeBSD system after all :rocket:)

# Software installation
1. Install FreeBSD, use ZFS as a file system, enable Unbound as your local DNS resolver.
2. Install required software:
```
pkg update
pkg install git nano python3 ansible
```
3. Clone the repo:
```
mkdir /root/pyVM/ && git clone https://github.com/yaroslav-gwit/PyVM-Bhyve.git /root/pyVM/
```


# Documentation
Would like to try out PyVM? Chech out the docs: https://github.com/yaroslav-gwit/PyVM-Bhyve/wiki
