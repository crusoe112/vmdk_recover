import argparse
import logging
import os
import re
import sys

VMDK_TEMPLATE = '''# Disk DescriptorFile
version=1
CID=d37878a6
parentCID=ffffffff
createType="twoGbMaxExtentSparse"

# Extent description
{}

# The Disk Data Base 
#DDB

ddb.adapterType = "ide"
ddb.encoding = "windows-1252"
ddb.geometry.cylinders = "{}"
ddb.geometry.heads = "16"
ddb.geometry.sectors = "63"
ddb.longContentID = "88ac9fad6dd46cf5aa161c50d37878a6"
ddb.toolsInstallType = "4"
ddb.toolsVersion = "12352"
ddb.virtualHWVersion = "4"'''

def get_dev_type(vm_dir, vm_files):
    vmx_file = [f for f in vm_files if f.endswith('.vmx')]

    if len(vmx_file) == 0:
        logging.error(' No VMX file found.')
        sys.exit(1)

    vmx_file = vmx_file[0]
    vmx_file = os.path.join(vm_dir, vmx_file)
    with open(vmx_file, 'r') as f:
        lines = f.readlines()
    for line in lines:
        reg = re.compile(r'scsi[0-9]+.virtualDev = "(.+)"')
        result = reg.search(line)
        if result:
            return result.group(1)

    logging.error(' No device type found.')
    sys.exit(1)

def get_all_vmdk_files(vm_files):
    reg = re.compile(r'-s([0-9]+)\.vmdk')
    vmdks = [f for f in vm_files if reg.search(f)]
    if len(vmdks) == 0:
        logging.error(' No VMDK files found.')
        sys.exit(1)
    return vmdks

def map_vmdk_file_lengths(vm_dir, vmdk_files):
    lengths = {}
    for vmdk_file in vmdk_files:
        vmdk_path = os.path.join(vm_dir, vmdk_file)
        size = os.path.getsize(vmdk_path)
        lengths[vmdk_file] = size
    return lengths

def create_extent_description_line(vmdk_file, length):
    return 'RW {} SPARSE "{}"'.format(length, vmdk_file)

def create_extent_description(vmdk_lengths):
    lines = []
    for vmdk_file, length in list(vmdk_lengths.items())[:-1]:
        lines.append(create_extent_description_line(vmdk_file, 4194304))
    lines.append(create_extent_description_line(list(vmdk_lengths.keys())[-1], list(vmdk_lengths.values())[-1] // 512))
    return '\n'.join(lines)

def get_cylinders(vmdk_lengths):
    CYLINDER_SIZE = 255 * 63 * 512
    total_size = sum(vmdk_lengths.values())
    return total_size // CYLINDER_SIZE

def fill_template(dev_type, extent_description, cylinders):
    return VMDK_TEMPLATE.format(extent_description, cylinders, dev_type)

def write_vmdk_file(output, content):
    with open(output, 'w') as f:
        f.write(content)

def main():
    args = argparse.ArgumentParser()
    args.add_argument('output', help='The output VMDK file')
    args.add_argument('--dir', help='The directory of the VM', default='.')
    args.add_argument('--verbosity', help='Verbosity level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO')
    args = args.parse_args()

    logging.basicConfig(level=args.verbosity)

    all_files = os.listdir(args.dir)
    logging.debug(' All files: {}'.format(all_files))

    # This was unnecessary for me, but I left it in case it is needed for someone else
    dev_type = get_dev_type(args.dir, all_files)
    logging.info(' Device type: {}'.format(dev_type))

    vmdk_files = get_all_vmdk_files(all_files)
    logging.info(' Found {} VMDK files.'.format(len(vmdk_files)))
    logging.debug(' VMDK files: {}'.format(vmdk_files))

    vmdk_lengths = map_vmdk_file_lengths(args.dir, vmdk_files)
    logging.debug(' VMDK file lengths: {}'.format(vmdk_lengths))

    extent_description = create_extent_description(vmdk_lengths)
    logging.info(' Extent description:\n{}'.format(extent_description))

    cylinders = get_cylinders(vmdk_lengths)
    logging.info(' Cylinders: {}'.format(cylinders))

    vmdk_content = fill_template(dev_type, extent_description, cylinders)
    logging.debug(' VMDK content:\n{}'.format(vmdk_content))
    
    logging.info(' Writing VMDK file to {}'.format(args.output))
    write_vmdk_file(args.output, vmdk_content)

if __name__ == '__main__':
    main()