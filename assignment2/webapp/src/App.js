import React, { useState, useEffect } from "react";
import "./App.css";
const XMLParser = require("react-xml-parser");

function App() {
  const [cimData, setCimData] = useState({});
  const [snmpData, setSnmpData] = useState({});
  const [useCim, setUseCim] = useState(true);

  useEffect(() => {
    const baseUrl = "http://129.241.209.11:5000";
    useCim
      ? Object.keys(cimData).length === 0 &&
        fetch(`${baseUrl}/cim_info`)
          .then(response => response.text())
          .then(response => {
            const xml = new XMLParser().parseFromString(response);
            console.log("xml", xml);
            setCimData(xml);
          })
          .catch(err => {
            console.log("fetch", err);
          })
      : Object.keys(snmpData).length === 0 &&
        fetch(`${baseUrl}/snmp_info`)
          .then(response => response.json())
          .then(response => {
            setSnmpData(response);
          })
          .catch(err => {
            console.log("fetch", err);
          });
  });

  const osData =
    cimData.children &&
    cimData.children[0].children.find(
      child => child.attributes.NAME === "Version"
    ).children[0].value;
  const ipData =
    cimData.children &&
    cimData.children[0].children.find(
      child => child.attributes.NAME === "IpInterfaces"
    ).children;

  console.log("State:");
  console.log("cimData", cimData);
  console.log("snmpData", snmpData);
  console.log("osData", osData);
  console.log("ipData", ipData);

  return (
    <div className="App">
      <header className="content">
        <div className="inputDataSelector">
          <div
            className={`${useCim ? "selected" : ""}`}
            onClick={() => setUseCim(true)}
          >
            CIM
          </div>
          <div
            className={`${!useCim ? "selected" : ""}`}
            onClick={() => setUseCim(false)}
          >
            SNMP
          </div>
        </div>

        {useCim ? (
          <div className="displayData">
            <h1>CIM Data</h1>
            <h2>OS</h2>
            <div className="dataTable osTable">
              {formatXMLOsData(osData || "")}
            </div>

            <h2>IP</h2>
            <div className="dataTable ipTable">
              <div className="tableRow">
                <span className="tableKey">Name</span>
                <span className="tableValue">IP Address</span>
                <span className="tableValue">Subnet Mask</span>
              </div>
              {(ipData || []).map(ipInterface =>
                formatXMLIpInterface(ipInterface)
              )}
            </div>
          </div>
        ) : (
          <div className="displayData">
            <h1>SNMP Data</h1>
            <h2>OS</h2>
            <div className="dataTable osTable">
              {formatJSONOsData(snmpData.os || "")}
            </div>

            <h2>IP</h2>

            <h2>IP</h2>
            <div className="dataTable ipTable">
              <div className="tableRow">
                <span className="tableKey">Name</span>
                <span className="tableValue">IP Address</span>
                <span className="tableValue">Subnet Mask</span>
              </div>
              {(snmpData.ipInterfaces || []).map(ipInterface =>
                formatJSONIpInterface(ipInterface)
              )}
            </div>
          </div>
        )}
      </header>
    </div>
  );
}

const formatXMLOsData = data => {
  const parsed = parseDataWithVaryingTuples(data);

  return Object.keys(parsed).map(key => {
    const value = parsed[key];
    return (
      <div className="tableRow">
        <span className="tableKey">{key}</span>
        <span className="tableValue">{value}</span>
      </div>
    );
  });
};

const formatXMLIpInterface = ipInterface => {
  console.log("ipInterface", ipInterface);
  const parsed = {};

  const name = ipInterface.children[0].children[0].value
    .split("=")[1]
    .replace('"', "")
    .replace('"', "");

  const ipAddr =
    ipInterface.children[1] &&
    ipInterface.children[1].children[0].value
      .split("=")[1]
      .replace('"', "")
      .replace('"', "");

  const subnetMask =
    ipInterface.children[2] &&
    ipInterface.children[2].children[0].value
      .split("=")[1]
      .replace('"', "")
      .replace('"', "");

  return (
    <div className="tableRow">
      <span className="tableKey">{name}</span>
      <span className="tableValue">{ipAddr}</span>
      <span className="tableValue">{subnetMask}</span>
    </div>
  );
};

const formatJSONOsData = osData => {
  console.log("osData", osData);
  return <div>{osData}</div>;
};

const formatJSONIpInterface = ipInterface => {
  console.log("formatJSONIpInterface", ipInterface);
  return <div>{ipInterface.address}</div>;
};

const parseDataWithVaryingTuples = data => {
  if (!data) return {};

  const splitIndexes = data
    .split("")
    .map((char, index) => (char === " " ? index : false))
    .filter(Boolean);

  const equalsIndexes = data
    .split("")
    .map((char, index) => (char === "=" ? index : false))
    .filter(Boolean);

  const desiredSplitIndexes = equalsIndexes
    .map(equalsIndex => {
      const lowerSpaceIndexes = splitIndexes.filter(i => i < equalsIndex);
      return lowerSpaceIndexes.length === 0
        ? false
        : Math.max(...lowerSpaceIndexes);
    })
    .filter(Boolean);

  const keyValuePairs = [];
  desiredSplitIndexes.forEach((splitIndex, loopIndex) => {
    const subStrStart =
      loopIndex === 0 ? 0 : desiredSplitIndexes[loopIndex - 1];
    keyValuePairs.push(data.substring(subStrStart, splitIndex));
  });

  keyValuePairs.push(
    data.substring(
      desiredSplitIndexes[desiredSplitIndexes.length - 1],
      data.length
    )
  );

  const parsed = {};

  keyValuePairs.map(keyValuePair => {
    const key = keyValuePair.split("=")[0].replace('"', "");
    const value = (keyValuePair.split("=")[1] || "")
      .replace('"', "")
      .replace("\\", "")
      .replace('"', "")
      .replace("\\", ""); // dont ask
    parsed[key] = value;
  });

  return parsed;
};

export default App;
