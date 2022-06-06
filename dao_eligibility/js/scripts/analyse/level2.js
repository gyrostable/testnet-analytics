const fs = require("fs");

const WRITE_FILES = false;

// Completing Arb ---------------------------------------
const arbCompleteEvents = require("../../data/arbComplete.json");

const arbCompleteAddresses = arbCompleteEvents.map((e) => e.args[0]);

WRITE_FILES &&
  fs.writeFileSync(
    "analysis/arbCompleteAddresses.json",
    JSON.stringify(arbCompleteAddresses)
  );

const mintAddresses = require("../../analysis/mintAddresses.json");

console.log("Addresses which completed arbitrage", arbCompleteAddresses.length);

console.log(
  "Mint addresses which completed arbitrage",
  arbCompleteAddresses.filter((address) => mintAddresses.includes(address))
    .length
);

// Buying NFTs ----------------------------------------
const nftBoughtEvents = require("../../data/nftBought.json");

const nftBoughtAddresses = nftBoughtEvents.map((e) => e.args[0]);

console.log("Addresses which bought NFT", nftBoughtAddresses.length);

console.log(
  "Mint addresses which bought NFT",
  nftBoughtAddresses.filter((address) => mintAddresses.includes(address)).length
);

WRITE_FILES &&
  fs.writeFileSync(
    "analysis/nftBoughtAddresses.json",
    JSON.stringify(nftBoughtAddresses)
  );
