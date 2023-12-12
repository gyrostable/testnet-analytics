const jonasFroggers = require("../data/jonasFroggers.json");
const joshSybilScores = require("../../analysis/sybilScores.json");

const jonasFroggersNum = jonasFroggers.length;
const joshSybilScoresNum = joshSybilScores.length;

let notFoundCountIndexes = [];
let sybilScoreMismatchIndexes = [];

for (
  let index = 0;
  index < Math.min(joshSybilScoresNum, jonasFroggersNum);
  index++
) {
  const { weighted_sybil_score, address } = jonasFroggers[index];
  const joshData = joshSybilScores.find(
    ({ address: joshAddress }) =>
      joshAddress.toLowerCase() === address.toLowerCase()
  );
  if (!joshData) {
    notFoundCountIndexes.push(index);
    continue;
  }

  if (weighted_sybil_score !== joshData["Weighted Sybil Score"]) {
    sybilScoreMismatchIndexes.push(index);
    continue;
  }
}

console.log(
  "Number of addresses in Jonas' data not found in Josh's data:",
  notFoundCountIndexes.length
);

console.log(
  "Number of addresses where weighted sybil scores do not match",
  sybilScoreMismatchIndexes.length
);

console.log(jonasFroggers[sybilScoreMismatchIndexes[0]]);
