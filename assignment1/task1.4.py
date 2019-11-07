import os
import time

time_between_checks = 60 * 2
packet_rate_per_sec_while_streaming = 400  # Guesstimate from observations.

THRESHOLD = time_between_checks * packet_rate_per_sec_while_streaming

previous_nr_of_packets = None

while True:
    print('Checking IP traffic...')
    command_to_get_IP_packets = 'snmpgetnext -v 2c -c ttm4128 localhost ipInReceives'
    ip_command_output = os.popen(command_to_get_IP_packets).read()
    total_nr_of_packets = int(ip_command_output.split(" ")[-1])
    packets_last_2_min = total_nr_of_packets - previous_nr_of_packets if previous_nr_of_packets is not None else 0
    print('packets_last_2_min', packets_last_2_min)

    if packets_last_2_min > THRESHOLD:
        print("nr_of_packets was over the threshold!")
        command_to_get_sysName = 'snmpgetnext -v 2c -c ttm4128 localhost sysName'
        sys_name = os.popen(command_to_get_sysName).read()

        trap_data = {
            'sysName': sys_name,
            'packets_last_2_min': packets_last_2_min
        }

        command_to_send_trap = 'snmptrap -v 2c -c ttm4128 localhost "" ntnuNotification ntnuNotification s "' +\
                               str(trap_data) + '"'

        os.system(command_to_send_trap)

    previous_nr_of_packets = total_nr_of_packets

    print("Sleeping until next check...")
    time.sleep(time_between_checks)
