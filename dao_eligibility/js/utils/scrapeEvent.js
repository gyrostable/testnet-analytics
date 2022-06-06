const fs = require("fs");

const scrapeEvent = async (
  contract,
  filter,
  startBlock,
  endBlock,
  filePath
) => {
  let allEvents = [];

  for (let i = startBlock - 1; i < endBlock + 1; i += 10000) {
    const _startBlock = i;
    console.log(
      _startBlock,
      " - ",
      Math.floor((endBlock - _startBlock) / 10000),
      " - ",
      allEvents.length
    );
    const _endBlock = Math.min(endBlock, i + 9999);
    const events = await contract.queryFilter(filter, _startBlock, _endBlock);
    allEvents = [...allEvents, ...events];
  }

  console.log(allEvents.length);

  fs.writeFileSync(filePath, JSON.stringify(allEvents));
};

module.exports = scrapeEvent;
