# Table of contents
- [pyVM Main commands](#pyvm-main-commands)
  * [VM listing and host information](#vm-listing-and-host-information)
  * [VM operations](#vm-operations)
  * [VM deployment](#vm-deployment)
  * [Currently supported Guest Operating Systems](#currently-supported-guest-operating-systems)

<br>

# pyVM Main commands
pyVM is a Bhyve VM manager. To get started type ```pyvm``` in your terminal, like in the example below.
```
root@hoster0101 ~# pyvm
╒════════════╤═══════════╤════════════════════╤══════════════╤══════════════╤═════════════╤═══════════╤════════════════╕
│ HostName   │ FreeRAM   │ Uptime             │   RunningVMs │ ZfsArcSize   │ ZfsStatus   │ ZfsFree   │ BackupStatus   │
╞════════════╪═══════════╪════════════════════╪══════════════╪══════════════╪═════════════╪═══════════╪════════════════╡
│ hoster0101 │ 22 GB     │ 3 hours 17 minutes │            2 │ 5023M        │ ONLINE      │ 1.75T     │ Local only     │
╘════════════╧═══════════╧════════════════════╧══════════════╧══════════════╧═════════════╧═══════════╧════════════════╛
╒════╤═══════════╤═════════════════╤══════════════╤═══════╤═══════╤═══════════╤══════════════════════╤════════════╤════════════╤════════════╤══════════════╤═════════════════╕
│    │ Name      │ State           │ Encryption   │   CPU │ RAM   │   VncPort │ VncPassword          │ DiskSize   │ DiskUsed   │ VmIpAddr   │ OsType       │ VmDescription   │
╞════╪═══════════╪═════════════════╪══════════════╪═══════╪═══════╪═══════════╪══════════════════════╪════════════╪════════════╪════════════╪══════════════╪═════════════════╡
│  1 │ test-vm-1 │ Running (97999) │ Encrypted    │     2 │ 1G    │      5900 │ CIUveH3ttLzu4Cevnfu8 │ 23G        │ 673M       │ 10.101.0.1 │ Ubuntu 20.04 │ -               │
├────┼───────────┼─────────────────┼──────────────┼───────┼───────┼───────────┼──────────────────────┼────────────┼────────────┼────────────┼──────────────┼─────────────────┤
│  2 │ test-vm-2 │ Running (21627) │ Encrypted    │     2 │ 1G    │      5901 │ SBbtG9ybz4pwithROiX2 │ 15G        │ 383M       │ 10.101.0.2 │ Debian 10    │ -               │
╘════╧═══════════╧═════════════════╧══════════════╧═══════╧═══════╧═══════════╧══════════════════════╧════════════╧════════════╧════════════╧══════════════╧═════════════════╛

```

<br>

## VM listing and host information
To check the general host information type this:
```
pyvm --hostinfo
```
Which in turn will output this table:
```
╒════════════╤═══════════╤════════════════════╤══════════════╤══════════════╤═════════════╤═══════════╤════════════════╕
│ HostName   │ FreeRAM   │ Uptime             │   RunningVMs │ ZfsArcSize   │ ZfsStatus   │ ZfsFree   │ BackupStatus   │
╞════════════╪═══════════╪════════════════════╪══════════════╪══════════════╪═════════════╪═══════════╪════════════════╡
│ hoster0101 │ 22 GB     │ 3 hours 17 minutes │            2 │ 5023M        │ ONLINE      │ 1.75T     │ Local only     │
╘════════════╧═══════════╧════════════════════╧══════════════╧══════════════╧═════════════╧═══════════╧════════════════╛
```
And this next command, will return a list of VMs:
```
pyvm --vmlist
```
This is the example output:
```
╒════╤═══════════╤═════════════════╤══════════════╤═══════╤═══════╤═══════════╤══════════════════════╤════════════╤════════════╤════════════╤══════════════╤═════════════════╕
│    │ Name      │ State           │ Encryption   │   CPU │ RAM   │   VncPort │ VncPassword          │ DiskSize   │ DiskUsed   │ VmIpAddr   │ OsType       │ VmDescription   │
╞════╪═══════════╪═════════════════╪══════════════╪═══════╪═══════╪═══════════╪══════════════════════╪════════════╪════════════╪════════════╪══════════════╪═════════════════╡
│  1 │ test-vm-1 │ Running (97999) │ Encrypted    │     2 │ 1G    │      5900 │ CIUveH3ttLzu4Cevnfu8 │ 23G        │ 673M       │ 10.101.0.1 │ Ubuntu 20.04 │ -               │
├────┼───────────┼─────────────────┼──────────────┼───────┼───────┼───────────┼──────────────────────┼────────────┼────────────┼────────────┼──────────────┼─────────────────┤
│  2 │ test-vm-2 │ Running (21627) │ Encrypted    │     2 │ 1G    │      5901 │ SBbtG9ybz4pwithROiX2 │ 15G        │ 383M       │ 10.101.0.2 │ Debian 10    │ -               │
╘════╧═══════════╧═════════════════╧══════════════╧═══════╧═══════╧═══════════╧══════════════════════╧════════════╧════════════╧════════════╧══════════════╧═════════════════╛
```

<br>

## VM operations
To start your VM use:
```
pyvm --vmstart test-vm-1
```
To stop your VM use:
```
pyvm --vmstop test-vm-1
```
To restart your VM use:
```
pyvm --vmrestart test-vm-1
```
To kill (forcefully stop) your VM use:
```
pyvm --vmkill test-vm-1
```
To destroy (delete/remove) your VM use:
```
pyvm --vmdestroy test-vm-1
```
To edit VM config (to change number of CPUs, or RAM size) use:
```
pyvm --vmedit test-vm-1
```
There are also commands to support mass operations:
```
pyvm --vmstartall
pyvm --vmkillall
pyvm --vmdestroyall
```

<br>

## VM deployment
If you need a test machine, just run this:
```
pyvm --vmdeploy
```
It will deploy the VM for you (Debian 10 by default), will assign it first available IP address and will use CloudInit to provision it.<br><br>
If you'd like to deploy a proper production VM, give ```pyvm --vmdeploy``` some more options:
```
pyvm --vmdeploy --vmname production-vm-01 --ostype ubuntu2004
```
I am still working on some of the other options, like static IP addressing, custom bridges, manual MAC address etc.<br>

<br>

## Currently supported Guest Operating Systems
```
FreeBSD 13 ZFS - freebsd13zfs  ## ZFS based image
FreeBSD 13 UFS - freebsd13ufs  ## UFS based image
Debian 10 - debian10
Debian 11 - debian11
Ubuntu Focal 20.04 - ubuntu2004
```
