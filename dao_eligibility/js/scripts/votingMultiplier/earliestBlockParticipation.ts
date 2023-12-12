const fs = require("fs");
const path = require("path");
const testnetChallengeBlockCompletion = require("../../data/testnetChallengeBlockCompletion.json");

const MIN_BLOCK_NUMBER = 20_000_000;

const WRITE_FILES = false;

const earliestBlockParticipation = {};

testnetChallengeBlockCompletion.forEach((data) => {
  if (typeof data.address !== "string" || data.address.slice(0, 2) !== "0x") {
    return;
  }
  [
    "block_number_lvl1_mint",
    "block_number_lvl1_lp",
    "block_number_lvl2_nft",
    "block_number_lvl2_full",
    "block_number_lvl25",
  ].forEach((key) => {
    if (
      data[key] > MIN_BLOCK_NUMBER &&
      (!earliestBlockParticipation[data.address] ||
        earliestBlockParticipation[data.address] > data[key])
    ) {
      earliestBlockParticipation[data.address] = data[key];
    }
  });
});

const filePath = `dao_eligibility/js/analysis/earliestBlockParticipation.json`;
const json = JSON.stringify(earliestBlockParticipation);
WRITE_FILES && fs.writeFileSync(filePath, json);
