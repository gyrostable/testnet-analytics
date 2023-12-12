const fs = require("fs");

const WRITE_FILES = false;
const LOG = true;

const filteredSybilScorers = require("../../analysis/filteredSybilScorers.json");

const newWeightedData = filteredSybilScorers.map((scorer) => {
  const componentWeightedScores = Object.values(
    scorer["Weight component scores"]
  );
  componentWeightedScores[0] = (componentWeightedScores[0] / 4) * 10;
  componentWeightedScores[2] = (componentWeightedScores[2] / 2) * 7;
  componentWeightedScores[5] = (componentWeightedScores[5] / 1) * 2;
  componentWeightedScores[4] = (componentWeightedScores[4] / 3) * 7;
  componentWeightedScores[3] = (componentWeightedScores[3] / 2) * 3;
  componentWeightedScores[15] = (componentWeightedScores[15] / 5) * 10;

  const newWeightedScore = componentWeightedScores.reduce(
    (acc, el) => acc + el,
    0
  );

  const earliestBlock = Object.keys(scorer)
    .filter((key) => key.includes("block_number"))
    .map((key) => scorer[key])
    .reduce((acc, el) => (el > 1 && el < acc ? el : acc), Infinity);

  const blockBonus =
    earliestBlock < 25250000 ? 25 : earliestBlock < 27000000 ? 10 : 0;

  const newTotalScore = newWeightedScore + blockBonus;

  const finalTier =
    newTotalScore >= 25
      ? 25
      : newTotalScore >= 15
      ? 10
      : newTotalScore >= 10
      ? 2
      : newTotalScore >= 1
      ? 1
      : 0;

  return {
    address: scorer.address,
    newWeightedScore,
    blockBonus,
    newTotalScore,
    finalTier,
  };
});

const freq = {};

newWeightedData.map(({ finalTier }) => {
  if (freq[finalTier]) {
    freq[finalTier]++;
  } else {
    freq[finalTier] = 1;
  }
});

LOG && console.log(freq);

const filePath = `dao_eligibility/js/analysis/newWeightedData.json`;
const json = JSON.stringify(newWeightedData);
WRITE_FILES && fs.writeFileSync(filePath, json);
