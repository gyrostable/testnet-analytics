const fs = require("fs");
const sybilScores = require("../../analysis/sybilScores.json");
const earliestBlockParticipation = require("../../analysis/earliestBlockParticipation.json");

const LOG_MESSAGES = true;
const WRITE_FILES = false;

// Remove participants with weighted sybil score <= 4
const filteredSybilScores = sybilScores.filter(
  (sybilScore) => sybilScore["Weighted Sybil Score"] > 4
);

LOG_MESSAGES &&
  console.log(
    `Removed ${
      sybilScores.length - filteredSybilScores.length
    } participants with weighted sybil score <= 4`
  );

const votingTierAndPoints = filteredSybilScores.map((sybilScore) => {
  const votingMulWeightedScore = weightVotingMultiplierScoreData(
    sybilScore["Unweighted component scores"]
  );
  const earliestBlockBonus = calculateEarliestBlockBonus(sybilScore.address);
  const totalVotingMultiplier = votingMulWeightedScore + earliestBlockBonus;
  const [finalTier, finalPoints] = calculateFinalTier(totalVotingMultiplier);

  return {
    address: sybilScore.address,
    "Weighted Sybil Score": sybilScore["Weighted Sybil Score"],
    "Voting Multiplier Weighted Score": votingMulWeightedScore,
    "Earliest Block Bonus": earliestBlockBonus,
    "Total Voting Multiplier Score": totalVotingMultiplier,
    "Final Tier": finalTier,
    "Final Voting Power Points": finalPoints,
  };
});

const filePath = `dao_eligibility/js/analysis/votingTierAndPoints.json`;
const json = JSON.stringify(votingTierAndPoints);

WRITE_FILES && fs.writeFileSync(filePath, json);

// ----------------------------------
// Utils ----------------------------
// ----------------------------------

function weightVotingMultiplierScoreData(scoreData) {
  let weightedScore = 0;
  weightedScore += Number(scoreData["4.1 In person POAP"]) * 10; // 4 -> 10
  weightedScore += Number(scoreData["4.2 Sybil.org list"]) * 3;
  weightedScore += Number(scoreData["4.3 Governance Voters"]) * 7; // 2 -> 7
  weightedScore += Number(scoreData["4.4.1 Community Calls"]) * 3; // 2 -> 3
  weightedScore += Number(scoreData["4.4.2 Strong Anti Sybil"]) * 7; // 3 -> 7
  weightedScore += Number(scoreData["4.4.3 Weak Anti Sybil"]) * 2; // 1 -> 2
  weightedScore +=
    Number(scoreData["4.5 Discord Challenge"]) +
    ({ 3: 2, 0: 0 }[scoreData["4.5 Discord Challenge"]] ?? 1);
  weightedScore += Number(scoreData["4.6.1 User Account Github"]) * 1;
  weightedScore += Number(scoreData["4.6.2 User Account Twitter"]) * 1;
  weightedScore += Number(scoreData["4.6.3 User Account Phone"]) * 2;
  weightedScore += Number(scoreData["4.7.1 More OAuths Stack Overflow"]) * 3;
  weightedScore += Number(scoreData["4.7.2 More OAuths Github"]) > 0 ? 3 : 0;
  weightedScore += Number(scoreData["4.7.3 More OAuths Twitter"]) > 0 ? 2 : 0;
  weightedScore += Number(scoreData["4.7.4 More OAuths Reddit"]) * 2;
  weightedScore += Number(scoreData["4.7.5 More OAuths Minecraft"]) * 1;
  weightedScore += Number(scoreData["4.8.1 Goldfinch KYC"]) * 10; // 5 -> 10
  weightedScore += Number(scoreData["4.8.2 Defi Whitelist"]) * 2;
  weightedScore += Number(scoreData["4.8.3 Coinbase"]) * 5;
  weightedScore += Number(scoreData["4.8.4: Discord"]) * 1;

  // Bonus points
  weightedScore += Number(scoreData["4.7.2 More OAuths Github"]) === 2 ? 1 : 0;
  weightedScore += Number(scoreData["4.7.3 More OAuths Twitter"]) === 2 ? 1 : 0;

  return weightedScore;
}

function calculateEarliestBlockBonus(address) {
  const earliestBlock = earliestBlockParticipation[address.toLowerCase()];

  if (earliestBlock && earliestBlock <= 25_250_000) return 25;
  if (earliestBlock && earliestBlock <= 27_000_000) return 10;
  return 0;
}

function calculateFinalTier(totalVotingMultiplier) {
  if (totalVotingMultiplier < 10) return [1, 1];
  if (totalVotingMultiplier < 15) return [2, 2];
  if (totalVotingMultiplier < 25) return [3, 10];
  return [4, 25];
}
