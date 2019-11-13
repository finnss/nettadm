import xmltodict
from flask import Flask, request, Response
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)
@app.route("/")
def index():
    return "Hello"


@app.route("/cim_info", methods=['GET'], strict_slashes=False)
def parse_request():
    command_to_get_OS = 'wbemcli ei http://ttm4128.item.ntnu.no:5988/root/cimv2:CIM_OperatingSystem -nl | grep Version'
    os_command_output = os.popen(command_to_get_OS).read()

    command_to_get_IP_names = 'wbemcli ei http://ttm4128.item.ntnu.no:5988/root/cimv2:CIM_IPProtocolEndpoint -nl | grep ElementName'
    command_to_get_IP_addresses = 'wbemcli ei http://ttm4128.item.ntnu.no:5988/root/cimv2:CIM_IPProtocolEndpoint -nl | grep IPv4Address'
    command_to_get_IP_mask = 'wbemcli ei http://ttm4128.item.ntnu.no:5988/root/cimv2:CIM_IPProtocolEndpoint -nl | grep SubnetMask'

    ip_names_command_output = os.popen(command_to_get_IP_names).read()
    ip_addr_command_output = os.popen(command_to_get_IP_addresses).read()
    ip_mask_command_output = os.popen(command_to_get_IP_mask).read()

    print('cim ip_names_command_output', ip_names_command_output)
    print('cim ip_addr_command_output', ip_addr_command_output)
    print('cim ip_mask_command_output', ip_mask_command_output)

    ip_names = ip_names_command_output.split('\n')[:-1]
    ip_addresses = ip_addr_command_output.split('\n')[:-1]
    ip_masks = ip_mask_command_output.split('\n')[:-1]

    print('cim ip_names', ip_names)
    print('cim ip_addresses', ip_addresses)
    print('cim ip_masks', ip_masks)

    xml_data = \
"""
<CIM CIMVERSION="2.0" DTDVERSION="2.0">
    <MESSAGE>
        <PROPERTY NAME="Version" TYPE="string">
            <VALUE>{}</VALUE>
        </PROPERTY>
        <PROPERTY NAME="IpInterfaces">
            INTERFACES_REPLACE
        </PROPERTY>
    </MESSAGE>
</CIM>
""".format(os_command_output)

    for i in range(len(ip_names)):
        name = ip_names[i].replace('-Element', '')
        address = ip_addresses[i].replace('-', '')
        ip_mask = ip_masks[i].replace('-', '')

        ip_interfaces_xml = """
            <PROPERTY NAME="IpInterface">
                <PROPERTY NAME="Name" TYPE="string">
                    <VALUE>{}</VALUE>
                </PROPERTY>
                <PROPERTY NAME="IPv4Address" TYPE="string">
                    <VALUE>{}</VALUE>
                </PROPERTY>
                <PROPERTY NAME="SubnetMask" TYPE="string">
                    <VALUE>{}</VALUE>
                </PROPERTY>
            </PROPERTY>
            INTERFACES_REPLACE
        """.format(name, address, ip_mask)

        xml_data = xml_data.replace('INTERFACES_REPLACE', ip_interfaces_xml)

    xml_data = xml_data.replace('INTERFACES_REPLACE', '')
    # parsed_os = xmltodict.parse(os_xml_data)
    # os_xml = xmltodict.unparse(parsed_os)

    # ip_xml = xmltodict.unparse(xmltodict.parse(ip_xml_data)).replace('<?xml version="1.0" encoding="utf-8"?>', '')
    # xml = xmltodict.unparse(xmltodict.parse(xml_data))
    xml = '<?xml version="1.0" encoding="utf-8"?>\n' + xml_data
    a = xmltodict.parse(xml_data)

    """
    xml_dict = {
        'MESSAGE': {
            'PROPERTY': {
                '@NAME': 'Version',
                '@TYPE': 'string',
                'VALUE': os_command_output
            },
            'PROPERTY': {
                '@NAME': 'IP_INTERFACES',
                'VALUE': [
                    {
                        'PROPERTY': {
                            '@NAME': 'Name',
                            '@TYPE': 'string',
                            'VALUE': ip_names_command_output
                        },
                        'PROPERTY': {
                            '@NAME': 'IPv4Address',
                            '@TYPE': 'string',
                            'VALUE': ip_addr_command_output
                        },
                        'PROPERTY': {
                            '@NAME': 'SubnetMask',
                            '@TYPE': 'string',
                            'VALUE': ip_mask_command_output
                        },
                    }
                ]
            }
        }
    }
    xml_to_return = xmltodict.unparse(xml_dict)
    """
    return Response(xml, mimetype='application/xml')


@app.route("/snmp_info", methods=['GET'], strict_slashes=False)
def parse_snmp_request():
    command_to_get_sysName = 'snmpgetnext -v 2c -c ttm4128 localhost sysDescr'
    sys_name = os.popen(command_to_get_sysName).read()

    NAME, VERSION, ID = parse_system_info(sys_name)
    os_json = {
        'NAME': NAME,
        'VERSION': VERSION,
        'ID': ID
    }

    command_to_get_IP_names = 'snmpwalk -v 2c -c ttm4128 localhost 1.3.6.1.2.1.2.2.1.2'
    command_to_get_IP_addresses = 'snmpwalk -v 2c -c ttm4128 localhost .1.3.6.1.2.1.4.20.1 | grep ipAdEntAddr'
    command_to_get_IP_mask = 'snmpwalk -v 2c -c ttm4128 localhost .1.3.6.1.2.1.4.20.1 | grep ipAdEntNetMask'

    ip_names_command_output = os.popen(command_to_get_IP_names).read()
    ip_addr_command_output = os.popen(command_to_get_IP_addresses).read()
    ip_mask_command_output = os.popen(command_to_get_IP_mask).read()

    print('snmp ip_names_command_output', ip_names_command_output)
    print('snmp ip_addr_command_output', ip_addr_command_output)
    print('snmp ip_mask_command_output', ip_mask_command_output)

    ip_names = ip_names_command_output.split('\n')[:-1]
    ip_addresses = ip_addr_command_output.split('\n')[:-1]
    ip_masks = ip_mask_command_output.split('\n')[:-1]

    print('snmp ip_names', ip_names)
    print('snmp ip_addresses', ip_addresses)
    print('snmp ip_masks', ip_masks)

    jsonResult = {
        'os': os_json,
        'ipInterfaces': []
    }

    for i in range(len(ip_addresses)):
        name = ip_names[i].split(" = ")[1].replace('STRING: ', '')
        address = ip_addresses[i].split(" ")[-1]
        mask = ip_masks[i].split(" ")[-1]

        jsonResult['ipInterfaces'] += [
            {
                'name': name,
                'address': address,
                'mask': mask
            }
        ]

    return Response(json.dumps(jsonResult), mimetype='application/json')


def parse_system_info(str):
    print('parsing input', str)
    list_of_words = str.split()

    NAME = list_of_words[list_of_words.index('STRING:') + 1]

    VERSION = list_of_words[list_of_words.index('STRING:') + 3]

    ID = list_of_words[list_of_words.index('STRING:') + 2]
    # ID_LIKE = list_of_words[list_of_words.index(ID) + 1]

    # PRETTY_NAME = list_of_words[list_of_words.index('') + 1]

    return NAME, VERSION, ID,  # ID_LIKE #, PRETTY_NAME

if __name__ == "__main__":
    app.run(host='0.0.0.0')