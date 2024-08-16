# Description
This script was intended to recover a missing VmWare Workstation vmdk descriptor file using the existing .vmx file and the actual .vmdk files. It cannot recover the actual data, only the descriptor file.
<br><br>
Taken from Broadcom article here: https://knowledge.broadcom.com/external/article/306526/recreating-a-missing-virtual-disk-vmdk-d.html
<br><br>
Currently, this will only work for 2GB Sparse formatted vmdk files. Feel free to contribute for other formats
<br><br>
This script is pretty specific to my own use case. You may need to modify the template and info to fit your needs. You can use another VM's .vmdk file as a template to get the correct values.
<br><br>
Be very careful with this script, especially when overwriting files. It is recommended to make a backup of the .vmx file and the .vmdk files before running this script.

# Usage
```shell
usage: vmdk_recover.py [-h] [--dir DIR] [--verbosity {DEBUG,INFO,WARNING,ERROR,CRITICAL}] output

positional arguments:
  output                The output VMDK file

options:
  -h, --help            show this help message and exit
  --dir DIR             The directory of the VM
  --verbosity {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Verbosity level
```

# Example
```shell
python vmdk_recover.py recovered.vmdk --dir c:\Path\To\Virtual\Machines\ubuntu --verbosity DEBUG
```

# Notes
- Make sure the .vmx file points to the new vmdk file
- Make sure the new vmdk file is in the same directory as the other vmdk files