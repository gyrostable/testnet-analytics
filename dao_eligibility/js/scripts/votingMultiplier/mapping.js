const fs = require("fs");
const newWeightedData = require("../../analysis/newWeightedData.json");
const mapping = require("../../data/addressMapping.json");

const WRITE_FILES = true;
const LOG = true;

const mappedData = newWeightedData.map((data) => {
  const mapData = mapping.find(
    ({ old }) => old.toLowerCase() === data.address.toLowerCase()
  );

  const mappedAddress = mapData ? mapData.new : data.address;

  return {
    ...data,
    address: mappedAddress,
  };
});

const duplicates = {};

const uniqueData = mappedData.filter((data, index) => {
  const _index = mappedData.findIndex(
    (_data) => _data.address.toLowerCase() === data.address.toLowerCase()
  );

  if (index !== _index) {
    if (duplicates[data.address.toLowerCase()]) {
      duplicates[data.address.toLowerCase()]++;
    } else {
      duplicates[data.address.toLowerCase()] = 1;
    }
  }

  return index === _index;
});

LOG && console.log("ORIGINAL LENGTH", mappedData.length);
LOG && console.log("UNIQUE LENGTH", uniqueData.length);

LOG && console.log(duplicates, Object.keys(duplicates).length);

const filePath = `dao_eligibility/js/analysis/uniqueWeightedData.json`;
const json = JSON.stringify(uniqueData);
WRITE_FILES && fs.writeFileSync(filePath, json);
