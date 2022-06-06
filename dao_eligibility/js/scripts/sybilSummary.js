const fs = require("fs");
const sybilScores = require("../analysis/sybilScores.json");
const keys = Object.keys(sybilScores[0]["Unweighted component scores"]);

const WRITE_FILES = true;

// TOTAL
const total = sybilScores.length;
console.log("SAMPLE TOTAL", total);
// Calculate number of passes per challenge --------------------
const numberOfPassesPerChallenge = {};

for (let key of keys) {
  numberOfPassesPerChallenge[key] = 0;
  sybilScores.forEach((datum) => {
    if (+datum["Unweighted component scores"][key] > 0) {
      numberOfPassesPerChallenge[key]++;
    }
  });
}

console.log(numberOfPassesPerChallenge);

// Calculate distribution of number of challenges passed -------

const distOfNumberOfChallengesPassed = {};

for (let datum of sybilScores) {
  let numberOfChallengesPassed = 0;
  for (let key of keys) {
    if (+datum["Unweighted component scores"][key] > 0)
      numberOfChallengesPassed++;
  }

  if (!distOfNumberOfChallengesPassed[String(numberOfChallengesPassed)])
    distOfNumberOfChallengesPassed[String(numberOfChallengesPassed)] = 1;
  else distOfNumberOfChallengesPassed[String(numberOfChallengesPassed)]++;
}

console.log(distOfNumberOfChallengesPassed);

// Calculate distribution of scores for each challenge -----------
const distributionOfScoresInAllChallenges = {};

for (let key of keys) {
  const challengeScoreDist = {};

  for (let datum of sybilScores) {
    const relevantScore = datum["Unweighted component scores"][key];

    if (!challengeScoreDist[String(relevantScore)]) {
      challengeScoreDist[String(relevantScore)] = 1;
    } else {
      challengeScoreDist[String(relevantScore)]++;
    }
  }

  distributionOfScoresInAllChallenges[key] = challengeScoreDist;
}

console.log(distributionOfScoresInAllChallenges);

// Calculate distribution of weighted sybil scores ------------
const distributionOfWeightedSybilScores = {};

for (let datum of sybilScores) {
  const score = datum["Weighted Sybil Score"];

  if (!distributionOfWeightedSybilScores[String(score)]) {
    distributionOfWeightedSybilScores[String(score)] = 1;
  } else {
    distributionOfWeightedSybilScores[String(score)]++;
  }
}

console.log(distributionOfWeightedSybilScores);

// FILES TO WRITE --------------------------------------------
if (WRITE_FILES) {
  fs.writeFileSync(
    "charts/numberOfPassesPerChallenge.json",
    JSON.stringify(numberOfPassesPerChallenge)
  );
  fs.writeFileSync(
    "charts/distOfNumberOfChallengesPassed.json",
    JSON.stringify(distOfNumberOfChallengesPassed)
  );
  fs.writeFileSync(
    "charts/distributionOfScoresInAllChallenges.json",
    JSON.stringify(distributionOfScoresInAllChallenges)
  );
  fs.writeFileSync(
    "charts/distributionOfWeightedSybilScores.json",
    JSON.stringify(distributionOfWeightedSybilScores)
  );
}
