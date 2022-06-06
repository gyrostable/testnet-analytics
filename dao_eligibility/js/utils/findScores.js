const { ethers } = require("ethers");

const findScores = (sybilChecksEvents, checkName) => {
  const subsetEvents = sybilChecksEvents.filter(
    (event) => event.args[0] === ethers.utils.formatBytes32String(checkName)
  );

  const addresses = [...new Set(subsetEvents.map((e) => e.args[1]))];

  const data = addresses.map((address) => {
    const events = subsetEvents.filter((event) => event.args[1] === address);
    const finalEvent = events[events.length - 1];
    const finalMetavalue = finalEvent.args[3];
    const score = ethers.BigNumber.from(finalMetavalue).toString();

    return {
      address,
      score,
    };
  });

  console.log(checkName, addresses.length);

  return data;
};

module.exports = findScores;
