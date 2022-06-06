const snapshot1VotersRaw = require("../../data/snapshot1Voters.json");
const snapshot2VotersRaw = require("../../data/snapshot2Voters.json");
const minters = require("../../analysis/mintAddresses.json");
const fs = require("fs");

const WRITE_FILES = false;

const snapshot1Voters = snapshot1VotersRaw.map(({ voter }) => voter);

const snapshot2Voters = snapshot2VotersRaw.map(({ voter }) => voter);

const votedInBoth = snapshot1Voters.filter((voter) =>
  snapshot2Voters.includes(voter)
);
const mintedAndVotedInBoth = minters.filter((minter) =>
  votedInBoth.includes(minter)
);

console.log("Voters in Snapshot Proposal 1", snapshot1Voters.length);
console.log("Voters in Snapshot Proposal 2", snapshot2Voters.length);
console.log("Voters in Snapshot proposal 1 and 2", votedInBoth.length);

console.log("Minters who voted in both proposals", mintedAndVotedInBoth.length);

WRITE_FILES &&
  fs.writeFileSync(
    "analysis/snapshot1Voters.json",
    JSON.stringify(snapshot1Voters)
  );

WRITE_FILES &&
  fs.writeFileSync(
    "analysis/snapshot2Voters.json",
    JSON.stringify(snapshot2Voters)
  );
