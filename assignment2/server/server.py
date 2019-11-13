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
    # os_command_output = "NAME=\"Ubuntu\" VERSION=\"14.04.6 LTS,Trusty Tahr\" ID=ubuntu ID_LIKE=debian PRETTY_NAME=\"Ubuntu 14.04.6 LTS\""

    command_to_get_IP_names = 'wbemcli ein http://ttm4128.item.ntnu.no:5988/root/cimv2:CIM_IPProtocolEndpoint -nl | grep Name'
    command_to_get_IP_addresses = 'wbemcli ein http://ttm4128.item.ntnu.no:5988/root/cimv2:CIM_IPProtocolEndpoint -nl | grep IPv4Address'
    command_to_get_IP_mask = 'wbemcli ein http://ttm4128.item.ntnu.no:5988/root/cimv2:CIM_IPProtocolEndpoint -nl | grep subnet'
    ip_names_command_output = os.popen(command_to_get_IP_names).read()
    ip_addr_command_output = os.popen(command_to_get_IP_addresses).read()
    ip_mask_command_output = os.popen(command_to_get_IP_mask).read()
    # ip_names_command_output = 'Name="IPv4_eth0"'
    # ip_addr_command_output = 'IPv4Address="129.241.200.173"'
    # ip_mask_command_output = 'SubnetMask="255.255.0.0"'

    xml_data = \
"""
<CIM CIMVERSION="2.0" DTDVERSION="2.0">
    <MESSAGE>
        <PROPERTY NAME="Version" TYPE="string">
            <VALUE>{}</VALUE>
        </PROPERTY>
        <PROPERTY NAME="IpInterfaces">
            <PROPERTY NAME="IpInterface0">
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
        </PROPERTY>
    </MESSAGE>
</CIM>
""".format(os_command_output, ip_names_command_output, ip_addr_command_output, ip_mask_command_output)
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

    command_to_get_IP_packets = 'snmpgetnext -v 2c -c ttm4128 localhost .1.3.6.1.2.1.4.20.1.1'
    ip_command_output = os.popen(command_to_get_IP_packets).read()

    jsonResult = {
        'os': sys_name,
        'ipInterfaces': ip_command_output
    }

    return Response(json.dumps(jsonResult), mimetype='application/json')


if __name__ == "__main__":
    app.run(host='0.0.0.0')