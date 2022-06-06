const fs = require("fs");

const WRITE_FILES = false;

// Mint -------------------------------------------------
const mintEvents = require("../../data/mintEvents.json");

const uniqueMintAddresses = [...new Set(mintEvents.map((e) => e.args[0]))];

console.log("Unique Mint addresses:", uniqueMintAddresses.length);

WRITE_FILES &&
  fs.writeFileSync(
    "analysis/mintAddresses.json",
    JSON.stringify(uniqueMintAddresses)
  );

// Join pool --------------------------------------------
const joinPoolEvents = require("../../data/joinPool.json");

const uniqueJoinPoolProxyAddresses = [
  ...new Set(joinPoolEvents.map((e) => e.args[0])),
];

console.log(
  "Unique Join Pool Proxy addresses:",
  uniqueJoinPoolProxyAddresses.length
);

WRITE_FILES &&
  fs.writeFileSync(
    "analysis/joinPoolProxyAddresses.json",
    JSON.stringify(uniqueJoinPoolProxyAddresses)
  );

// Match minters to proxy addresses ----------------------

console.log(uniqueJoinPoolProxyAddresses.length);

const minterToProxyMap = require("../../analysis/minterToProxyMap.json");
const minters = require("../../analysis/mintAddresses.json");

const mintersWithProxyAddresses = minters.filter(
  (minter) => minterToProxyMap[minter]
);

console.log("Minters with proxy addresses:", mintersWithProxyAddresses.length);

const poolJoiners = mintersWithProxyAddresses.filter((minter) =>
  uniqueJoinPoolProxyAddresses.includes(minterToProxyMap[minter])
);

console.log("Pool joiners", poolJoiners.length);

WRITE_FILES &&
  fs.writeFileSync("analysis/poolJoiners.json", JSON.stringify(poolJoiners));
