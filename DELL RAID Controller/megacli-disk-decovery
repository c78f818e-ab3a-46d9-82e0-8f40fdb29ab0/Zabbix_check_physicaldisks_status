#!/usr/bin/python

import os
import re
from sys import argv, exit
import argparse


def exiterror(msg, error_code=2):
    '''
    Exit with a specific error code (default 2)
    :msg: Message to be returned
    :error_code: Exit code
    '''
    print 'ERROR - ' + msg
    exit(error_code)


def get_output(flags):
    '''
    Execute megacli with the specified flags and return the output
    Assumes that none of the keys in the output has a colon (:) in the name
    :flags: flags for megacli
    :return: a dictionary with the output of the command
    '''
    cmd = binarypath + ' ' + flags
    output = os.popen(cmd).read()
    lines = []
    for line in output.split('\n'):
        if ':' in line:
            k, v = line.split(':', 1)
            lines += [(k.strip(), v.strip())]
    return lines


def get_info(key, input, output_format='string'):
    '''
    Extract information from the output of get_output
    :key: the regexp for the needed key
    :input: output from get_output
    :output_format: preferred output format (list or string)
    :return: the requested information as a list or string
    '''
    res = []
    try:
        for elem in input:
            if re.match(key, elem[0]):
                if output_format == 'string':
                    return elem[1]
                else:
                    res.append(elem[1])
        return res
    except KeyError:
        print 'ERROR - Key {0} not found'.format(key)
        exit(2)


binarypath = '/usr/sbin/megacli'
something_is_wrong = False

# Cau truc du lieu lay dc
# {'c0': {'arrays': {'c0u0': ['drives_number', 'RAID1', '465G', 'Optimal', 'None'],
#                    'c0u1': ['drives_number', 'RAID1', '465G', 'Optimal', 'None']},
#         'disks': [[controller_number,
#                    virtual_disk,
#                    disk_id,
#                    serial_number,
#                    status],
#                   [controller_number,
#                    virtual_disk,
#                    disk_id,
#                    serial_number,
#                    status],
#                   [controller_number,
#                    virtual_disk,
#                    disk_id,
#                    serial_number,
#                    status],
#                   [controller_number,
#                    virtual_disk,
#                    disk_id,
#                    serial_number,
#                    status]],
#         'model': model}}

# Tu cac thong tin tren, ta se chi xuat ra cac thong tin cua disk

resulting_info = {}

    # Get the number of controllers
    output = get_output('-adpCount -NoLog')
    controllers_number = int(get_info('Controller Count', output).rstrip
    controllers = ['c' + str(a) for a in range(controllers_number)]
# Start collecting info about the controllers
for controller_id in controllers:
    controller_number = controller_id.lstrip('c')
    output = get_output('-AdpAllInfo -a{0} -NoLog'.format(controller_number))
    controllermodel = get_info('Product Name', output)
    resulting_info[controller_id] = {}
    resulting_info[controller_id]['model'] = controllermodel
    # Now for the array info
    output = get_output('-LdGetNum -a{0} -NoLog'.format(controller_number))
    arrays_number = int(get_info(r'^Number of Virtual (Disk|Drive).*$',
                                 output))
    resulting_info[controller_id]['arrays'] = {}
    for array_number in range(arrays_number):
        # Temporary list to store information for each array
        # Format: [drives_number, raid_type, size, state, operation]
        this_array = []
        array_id = 'c{0}u{1}'.format(controller_number, array_number)
        output = get_output('-LDInfo -l{0} -a{1} -NoLog'.format(array_number,
                            controller_number))
        drives_number = get_info(r'Number Of Drives\s*((per span))?', output)
        if not drives_number:
            exiterror('Cannot any drives in array ' + array_id)

        span_depth = get_info('Span Depth', output)
        if not span_depth:
            exiterror('Invalid span depth for array' + array_id)

        raid_level_string = get_info('RAID Level', output)
        if not raid_level_string:
            exiterror('Cannot fetch raid level for array ' + array_id)
        # Extract the raid level
        raid_level = raid_level_string.split(',')[0].split('-')[1]
        raid_type = 'RAID' + raid_level
        # Not too sure what this does
        if drives_number and (int(span_depth) > 1):
            drives_number = int(drives_number) * int(span_depth)
            if int(raid_level) < 10:
                raid_type = raid_type + "0"

        size = get_info('Size', output)
        if not size:
            exiterror('Cannot fetch size for drive ', )
        if 'MB' in size:
            size = str(int(round((float(size.rstrip(' MB')) / 1000)))) + 'G'
        elif 'TB' in size:
            size = str(int(round((float(size.rstrip(' TB')) * 1000)))) + 'G'
        else:
            size = str(int(round((float(size.rstrip(' GB')))))) + 'G'

        state = get_info('State', output)
        if state != 'Optimal':
            something_is_wrong = True

        operation = get_info('Ongoing Progresses', output)
        if operation:
            # We need the following line for the description of what's going on
            operation = [output[output.index(tup) + 1] for tup in output
                            if tup[0] == 'Ongoing Progresses']
        if not operation:
            operation = 'None'

        this_array = [str(drives_number), raid_type, size, state, operation]
        resulting_info[controller_id]['arrays'][array_id] = this_array
    # Finally moving to physical disks
    resulting_info[controller_id]['disks'] = []
    output = get_output('-LdPdInfo -a{0} -NoLog'.format(controller_number))
    # There can be different enclosures attached to the same controller
    enclosure_numbers = get_info('Enclosure Device ID', output, 'list')
    slot_numbers = get_info('Slot Number', output, 'list')
    disk_identifiers = [a.split()[0] for a in get_info(r'PD$', output, 'list')]
    slots_list = zip(enclosure_numbers, slot_numbers, disk_identifiers)

    for enclosure_number, slot_id, disk_id in slots_list:
        if not enclosure_number or enclosure_number == 'N/A':
            exiterror('Cannot fetch enclosure ID for drive {0} on ' +
                        'controller {1}'.format(disk_id, controller_number))
        output = get_output('-PDInfo -PhysDrv \[{0}:{1}\] -a{2}'.format(
                            enclosure_number, slot_id, controller_number))
        disk_temperature = get_info('Drive Temperature', output).split()[0][:-1]
        state = get_info('Firmware state', output)
        if state not in ['Online', 'Online, Spun Up']:
            something_is_wrong = True

        model = re.sub(r'\s+', ' ', get_info('Inquiry Data', output))

        # Sometimes a typo is returned. For real.
        virtual_disk_string = get_info("Drive's position", output)
        if not virtual_disk_string:
            virtual_disk_string = get_info("Drive's postion", output)

        virtual_disk = virtual_disk_string.split(',')[0].split()[1]
        resulting_info[controller_id]['disks'].append(
            [str(controller_number), virtual_disk, disk_id, model, state, disk_temperature, slot_id])


# Xuat  ra vi tri cua disk tren server theo dinh dang file Json cho Zabbix Server
    # Keep count
    first = 1
    print "{"
    print "\t\"data\":[\n"
    for controller in sorted(resulting_info.keys()):
        for disk in sorted(resulting_info[controller]['disks']):
            a = disk[6]
            if not first:
               print "\t,"
            print "\t{"
            print '\t\t"{#DISK}"'':''"%s"' %(disk[6],)
            print "\n\t}"
            first = 0


    print "\n\t]"
    print "}\n"
