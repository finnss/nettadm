import xmltodict
from flask import Flask, request, Response
import os

app = Flask(__name__)
@app.route("/")
def index():
    return "Hello"


@app.route("/cim_info", methods=['POST', 'GET'], strict_slashes=False)
def parse_request():
    command_to_get_OS = 'wbemcli ei http://ttm4128.item.ntnu.no:5988/root/cimv2/CIM_OperatingSystem -dx -nl | grep Version'
    # os_command_output = os.popen(command_to_get_OS).read()
    os_command_output = "NAME=\"Ubuntu\" VERSION=\"14.04.6 LTS,Trusty Tahr\" ID=ubuntu ID_LIKE=debian PRETTY_NAME=\"Ubuntu 14.04.6 LTS\""
    xml_data = \
"""
<PROPERTY NAME="Version" TYPE="string">
<VALUE>someValue</VALUE>
</PROPERTY>
"""
    parsed = xmltodict.parse(xml_data)
    os_data = {
        'PROPERTY': {
            '@NAME': 'Version',
            '@TYPE': 'string',
            'VALUE': os_command_output
        }
    }
    xml = xmltodict.unparse(os_data)
    # content = xmltodict.parse(request.get_data())
    # print(content)
    return Response(xml, mimetype='application/xml')


if __name__ == "__main__":
    app.run(host='0.0.0.0')