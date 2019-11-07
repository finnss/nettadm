import os
import time
import json
import smtplib
import ssl

time_between_checks = 60
send_email_every_x_minutes = 5
packet_rate_per_sec_while_streaming = 400  # Guesstimate from observations
THRESHOLD = time_between_checks * packet_rate_per_sec_while_streaming

agent_addresses = [
    # '192.168.0.205',
    '192.168.0.203'
]

previous_nr_of_packets = None
previous_timestamp = time.time()

"""
Format: 
exceeded_threshold = {
    agent_address: [
        { scan_end_threshold: timestamp, packets_last_min: int},  # Only added if packets_last_min > THRESHOLD. Reset every 5 min.
        ...
    ],
    ...
}
"""
exceeded_threshold = {}
password = input("Type your password and press enter: ")


def send_email():
    print('mail', json.dumps(exceeded_threshold, 2))

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "test.nettadm.ass1@gmail.com"  # Enter your address
    receiver_email = "ttm4128@item.ntnu.no"  # Enter receiver address
    message = "From: Group 4\nSubject: SNMP Packet report from Group 4\n\n"

    message += "Hey! Here's your report for which agents received more packets than usual in this period.\n" \
        if len(exceeded_threshold.keys()) > 0 else "Hey! No agents received an usual amount of IP packets this period."

    for agent in exceeded_threshold.keys():
        message += "{}:\n".format(agent)

        for packet_breach in exceeded_threshold[agent]:
            message += "\tPackets this breach: {}\n\tTime of the scan: {}\n\n".format(packet_breach['packets_last_min'],
                                                                                      packet_breach['scan_end_timestamp'])

    context = ssl.create_default_context()
    print("Sending mail...\n", message)
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

    print("Mail sent")


while True:
    # Reset Data after a mail is sent.
    exceeded_threshold = {
      "192.168.0.205": [
        {
          "scan_end_timestamp": "Tue Oct  1 19:33:05 2019",
          "packets_last_min": 5745
        },
        {
          "scan_end_timestamp": "Tue Oct  1 18:34:05 2019",
          "packets_last_min": 8000
        },
        {
          "scan_end_timestamp": "Tue Oct  1 18:35:05 2019",
          "packets_last_min": 4807
        },
        {
          "scan_end_timestamp": "Tue Oct  1 18:36:05 2019",
          "packets_last_min": 6123
        }

      ]
    }
    for agent_address in agent_addresses:
        exceeded_threshold[agent_address] = []

    # Each iteration of this loop is the scan done every minute
    for i in range(send_email_every_x_minutes):
        print('Checking IP traffic...')

        # Each minute, scan each agent. If they received a lot of packets, add that data to
        for agent_address in agent_addresses:
            print('Scanning agent at address {}'.format(agent_address))

            command_to_get_IP_packets = 'snmpgetnext -v 2c -c ttm4128 {} ipInReceives'.format(agent_address)
            ip_command_output = os.popen(command_to_get_IP_packets).read()
            total_nr_of_packets = int(ip_command_output.split(" ")[-1])
            packets_last_min = total_nr_of_packets - previous_nr_of_packets if previous_nr_of_packets is not None else 0
            print('packets_last_min', packets_last_min)

            if packets_last_min > THRESHOLD:
                print("nr_of_packets was over the threshold! ({})".format(THRESHOLD))
                exceeded_threshold[agent_address] += [{
                    'scan_end_timestamp': time.ctime(),
                    'packets_last_min': packets_last_min
                }]

            previous_nr_of_packets = total_nr_of_packets

        print("Sleeping until next check...")
        time.sleep(time_between_checks)

    send_email()


