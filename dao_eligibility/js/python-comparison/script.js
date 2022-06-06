let data = require("./data/challenge-progression-stats-details.json");
const fs = require("fs");
const ethers = require("ethers");

// Remove blacklist addresses
const BLACK_LIST_ADDRESSES = [
  // Josh test addresses
  "0x729A1aECF890AAcF517B0E83764dd64dADe98480",
  "0xB337CeEb317B9Ab7D99Bfa9909fD7eF61b42b292",
  "0xf329462556d2d088b0B163beC9DdC1290bb43e1B",
  "0x517e23e42a200bC2F0eA718601876c5ea3663c41",
  "0xDB8F503eD292C65D6d233b7297736779047190A7",
  "0x615Cf1e3032836AFb76f096350b1a0bBA7202708",
  "0x749a8524b283Dc723F5A86387b293580fa7ebA01",
  "0x3d9C3c80C80F1EC1e9eF98BA4230ef0259045531",
  "0x59F0FfB87065aBFFB493F0a9398f98744075eF66",
  "0xF753c26454D46457088A2eE790D4a000cb4efFA0",
  "0x59F0FfB87065aBFFB493F0a9398f98744075eF66",
];

data = data.filter(
  ({ address }) =>
    !BLACK_LIST_ADDRESSES.some(
      (blacklistAddress) =>
        ethers.utils.getAddress(blacklistAddress) ===
        ethers.utils.getAddress(address)
    )
);

// // Normalize scores

// data.forEach((datum) => {
//   datum["ch_7_twitter"] =
//     { 4: 2, 3: 2, 2: 1 }[Number(datum["ch_7_twitter"])] || 0;

//   datum["ch_7_git"] = { 3: 2, 2: 1, 1: 1 }[Number(datum["ch_7_git"])] || 0;
// });

const challengeNames = Object.keys(data[0]).filter(
  (string) => string.slice(0, 2) === "ch"
);

const challengeScoreDists = {};

challengeNames.forEach((challengeName) => {
  if (!challengeScoreDists[challengeName])
    challengeScoreDists[challengeName] = {};

  data.forEach((datum) => {
    if (!datum[challengeName]) return;
    if (!challengeScoreDists[challengeName][datum[challengeName]])
      challengeScoreDists[challengeName][datum[challengeName]] = 0;

    challengeScoreDists[challengeName][datum[challengeName]]++;
  });
});

const challengeCounts = {};

challengeNames.forEach((challengeName) => {
  if (!challengeCounts[challengeName]) challengeCounts[challengeName] = 0;

  data.forEach((datum) => {
    if (!datum[challengeName]) return;
    challengeCounts[challengeName]++;
  });
});

// console.log(challengeScoreDists);
// console.log(challengeCounts);

// Weight function

data.forEach((datum) => weightScoreData(datum));

const weightedChallengeNames = Object.keys(data[0])
  .filter((string) => string.slice(0, 2) === "w_")
  .concat(["github_bonus", "twitter_bonus"]);

const weightedChallengeScoreDists = {};

weightedChallengeNames.forEach((challengeName) => {
  if (!weightedChallengeScoreDists[challengeName])
    weightedChallengeScoreDists[challengeName] = {};

  data.forEach((datum) => {
    if (!datum[challengeName]) return;
    if (!weightedChallengeScoreDists[challengeName][datum[challengeName]])
      weightedChallengeScoreDists[challengeName][datum[challengeName]] = 0;

    weightedChallengeScoreDists[challengeName][datum[challengeName]]++;
  });
});

// console.log(weightedChallengeScoreDists);

// Filter data

data = data.filter(sybilFilter);

// Dist of weighted scores
const weightedScoresDist = {};

data.forEach((datum) => {
  if (!weightedScoresDist[datum.weightedScore])
    weightedScoresDist[datum.weightedScore] = 0;
  weightedScoresDist[datum.weightedScore]++;
});

console.log(weightedScoresDist);

const buckets = { 1: 0, 2: 0, 3: 0, 4: 0 };

Object.entries(weightedScoresDist).map(([key, value]) => {
  if (key <= 3) return (buckets[1] += value);
  if (key <= 8) return (buckets[2] += value);
  if (key <= 15) return (buckets[3] += value);
  return (buckets[4] += value);
});

console.log(buckets);

// Remove unnecessary fields

data.forEach((datum) => {
  delete datum.FIELD1;
  delete datum.sybil_score;
});

// fs.writeFileSync(
//   "daniel-comparison/analysis/finalData.json",
//   JSON.stringify(data)
// );

function weightScoreData(scoreData) {
  let weightedScore = 0;
  weightedScore += Number(scoreData["ch_1"]) * 4;
  scoreData["w_ch_1"] = Number(scoreData["ch_1"]) * 4;

  weightedScore += Number(scoreData["ch_2"]) * 3;
  scoreData["w_ch_2"] = Number(scoreData["ch_2"]) * 3;

  weightedScore += Number(scoreData["ch_3"]) * 2;
  scoreData["w_ch_3"] = Number(scoreData["ch_3"]) * 2;

  weightedScore += Number(scoreData["ch_4_comm"]) * 2;
  scoreData["w_ch_4_comm"] = Number(scoreData["ch_4_comm"]) * 2;

  weightedScore += Number(scoreData["ch_4_strong"]) * 3;
  scoreData["w_ch_4_strong"] = Number(scoreData["ch_4_strong"]) * 3;

  weightedScore += Number(scoreData["ch_4_weak"]) * 1;
  scoreData["w_ch_4_weak"] = Number(scoreData["ch_4_weak"]) * 1;

  weightedScore += { 3: 5, 2: 3, 1: 2 }[Number(scoreData["ch_5"])] || 0;
  scoreData["w_ch_5"] = { 3: 5, 2: 3, 1: 2 }[Number(scoreData["ch_5"])] || 0;

  weightedScore += Number(scoreData["ch_6_github"]) * 1;
  scoreData["w_ch_6_github"] = Number(scoreData["ch_6_github"]) * 1;

  weightedScore += Number(scoreData["ch_6_twitter"]) * 1;
  scoreData["w_ch_6_twitter"] = Number(scoreData["ch_6_twitter"]) * 1;

  weightedScore += Number(scoreData["ch_6_phone"]) * 2;
  scoreData["w_ch_6_phone"] = Number(scoreData["ch_6_phone"]) * 2;

  weightedScore += Number(scoreData["ch_7_stack"]) * 3;
  scoreData["w_ch_7_stack"] = Number(scoreData["ch_7_stack"]) * 3;

  weightedScore += Number(scoreData["ch_7_git"]) > 0 ? 2 : 0;
  scoreData["w_ch_7_git"] = Number(scoreData["ch_7_git"]) > 0 ? 2 : 0;

  weightedScore += Number(scoreData["ch_7_twitter"]) > 0 ? 1 : 0;
  scoreData["w_ch_7_twitter"] = Number(scoreData["ch_7_twitter"]) > 0 ? 1 : 0;

  weightedScore += Number(scoreData["ch_7_reddit"]) * 2;
  scoreData["w_ch_7_reddit"] = Number(scoreData["ch_7_reddit"]) * 2;

  weightedScore += Number(scoreData["ch_7_minecraft"]) * 1;
  scoreData["w_ch_7_minecraft"] = Number(scoreData["ch_7_minecraft"]) * 1;

  weightedScore += Number(scoreData["ch_8_goldfinch"]) * 5;
  scoreData["w_ch_8_goldfinch"] = Number(scoreData["ch_8_goldfinch"]) * 5;

  weightedScore += Number(scoreData["ch_8_defiwl"]) * 2;
  scoreData["w_ch_8_defiwl"] = Number(scoreData["ch_8_defiwl"]) * 2;

  weightedScore += Number(scoreData["ch_8_coinbase"]) * 5;
  scoreData["w_ch_8_coinbase"] = Number(scoreData["ch_8_coinbase"]) * 5;

  weightedScore += Number(scoreData["ch_8_contributors"]) * 1;
  scoreData["w_ch_8_contributors"] = Number(scoreData["ch_8_contributors"]) * 1;

  // Twitter / Github match conditions
  const twitterMatch = scoreData["ch_7_twitter"] >= 3;

  const githubMatch = scoreData["ch_7_git"] >= 3;

  // Bonus points
  weightedScore += githubMatch ? 3 : 0;
  scoreData["github_bonus"] = githubMatch ? 3 : 0;

  weightedScore += twitterMatch ? 3 : 0;
  scoreData["twitter_bonus"] = twitterMatch ? 3 : 0;

  scoreData["weightedScore"] = weightedScore;

  return weightedScore;
}

function sybilFilter(datum) {
  return (
    (datum.passed_levels > 0 && datum.weightedScore >= 5) ||
    (datum.passed_levels > 4 && datum.weightedScore > 0)
  );
}
