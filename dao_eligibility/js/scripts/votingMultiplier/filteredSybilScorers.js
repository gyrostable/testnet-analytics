const fs = require("fs");
const weightedSybilScores = require("../../analysis/weightedSybilScores.json");
const testnetChallengeBlockCompletion = require("../../data/testnetChallengeBlockCompletion.json");

const LOG = true;
const WRITE_FILES = true;

LOG && console.log("Total sybil scorers:", weightedSybilScores.length);

const filteredWeightedSybilScorers = weightedSybilScores.filter((scorer) => {
  const data = testnetChallengeBlockCompletion.find(
    (data) => data.address.toLowerCase() === scorer.address.toLowerCase()
  );
  if (!data) return false;

  let passedLevelCount = 0;

  Object.entries(data).map(([key, val]) => {
    if (key === "index" || key === "address") return;
    if (val > 0) passedLevelCount++;
  });

  const weightedSybilScore = scorer["Weighted Sybil Score"];

  const condition1 = weightedSybilScore > 4 && passedLevelCount > 0;
  const condition2 = weightedSybilScore > 0 && passedLevelCount > 4;

  return condition1 || condition2;
});

const filteredSybilScorers = filteredWeightedSybilScorers.map((scorer) => {
  const challengeCompletionData = testnetChallengeBlockCompletion.find(
    (data) => data.address.toLowerCase() === scorer.address.toLowerCase()
  );

  const finalData = {
    ...scorer,
    ...challengeCompletionData,
  };

  delete finalData.index;

  return finalData;
});

LOG && console.log("Filtered sybil scorers:", filteredSybilScorers.length);

const filePath = `dao_eligibility/js/analysis/filteredSybilScorers.json`;
const json = JSON.stringify(filteredSybilScorers);
WRITE_FILES && fs.writeFileSync(filePath, json);
