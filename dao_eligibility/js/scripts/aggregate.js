const minters = require("../analysis/mintAddresses.json");
const poolJoiners = require("../analysis/poolJoiners.json");
const arbers = require("../analysis/arbCompleteAddresses.json");
const nftBuyers = require("../analysis/nftBoughtAddresses.json");
const proposal1Voters = require("../analysis/snapshot1Voters.json");
const proposal2Voters = require("../analysis/snapshot2Voters.json");
const sybilScores = require("../analysis/sybilScores.json");
const findIntersect = require("../utils/findIntersect");
const fs = require("fs");

const mintAndJoinPool = findIntersect(minters, poolJoiners);
const mintAndArb = findIntersect(mintAndJoinPool, arbers);
const mintAndBuyNFT = findIntersect(mintAndArb, nftBuyers);

const mintAndVote1 = findIntersect(mintAndBuyNFT, proposal1Voters);
const mintAndVote2 = findIntersect(mintAndBuyNFT, proposal2Voters);
const mintAndVoteEither = [...new Set([...mintAndVote1, ...mintAndVote2])];

const sybilAddresses = sybilScores.map(({ address }) => address);
console.log(sybilAddresses.length);

const sybilParticipants = findIntersect(mintAndVoteEither, sybilAddresses);

console.log("\n");
console.log("Number of:");
console.log("\n");

console.log("Minters:", minters.length);
console.log("- of which joined SAMM", mintAndJoinPool.length);
console.log("  - of which conducted arbitrage:", mintAndArb.length);
console.log("    - of which bought NFT:", mintAndBuyNFT.length);
console.log(
  "      - of which voted in either proposal:",
  mintAndVoteEither.length
);
console.log(
  "        - of which got at least 1 point in Sybil challenges",
  sybilParticipants.length
);

const summaryData = {
  minters: minters.length,
  "of which joined SAMM": mintAndJoinPool.length,
  "of which conducted arbitrage": mintAndArb.length,
  "of which bought NFT": mintAndBuyNFT.length,
  "of which voted in either proposal": mintAndVoteEither.length,
  "of which got at least 1 point in Sybil challenges": sybilParticipants.length,
};

fs.writeFileSync("analysis/summary.json", JSON.stringify(summaryData));

// const votersInEitherProposal = [
//   ...new Set([...proposal1Voters, ...proposal2Voters]),
// ];

// // const masterData = minters.map((minter, index) => {
// //   console.log(index + " out of " + minters.length);

// //   const joinedPool = poolJoiners.includes(minter);
// //   const conductedArbitrage = arbers.includes(minter);
// //   const boughtNft = nftBuyers.includes(minter);
// //   const voted = votersInEitherProposal.includes(minter);
// //   const scoredInSybilChallenges = sybilParticipants.includes(minter);

// //   const returnObj = {
// //     address: minter,
// //     joinedPool,
// //     conductedArbitrage,
// //     boughtNft,
// //     voted,
// //     scoredInSybilChallenges,
// //   };

// //   if (scoredInSybilChallenges) {
// //     const scoreData = sybilScores.find(({ address }) => address === minter);

// //     returnObj.unweightedScores = scoreData["Unweighted component scores"];
// //     returnObj.weightedSybilScore = scoreData["Weighted Sybil Score"];
// //   }

// //   return returnObj;
// // });

// // fs.writeFileSync("analysis/masterData.json", JSON.stringify(masterData));
