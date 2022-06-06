const { ethers, BigNumber } = require("ethers");
const data = require("../../data/sybilChecks.json");
const fs = require("fs");

const parsedData = data.map((datum) => ({
  address: datum.args[1],
  challenge: findChallengeName(ethers.utils.parseBytes32String(datum.args[0])),
  score: BigNumber.from(datum.args[3]).toString(),
  blockNumber: datum.blockNumber,
}));

const dataObj = {};

parsedData.forEach((datum) => {
  const key = datum.address + datum.challenge;

  if (!dataObj[key] || datum.blockNumber > dataObj[key].blockNumber) {
    dataObj[key] = datum;
  }
});

const finalData = Object.values(dataObj);

const challengeNames = [
  ...new Set(finalData.map(({ challenge }) => challenge)),
];

function findChallengeName(challengeName) {
  if (challengeName === "github-standardised") return "github";
  if (challengeName === "twitter-standardised") return "twitter";

  return challengeName;
}

const finalScoreDist = {};

finalData.forEach(({ challenge, score }) => {
  if (!finalScoreDist[challenge]) finalScoreDist[challenge] = {};
  if (!finalScoreDist[challenge][score]) finalScoreDist[challenge][score] = 1;
  else {
    finalScoreDist[challenge][score]++;
  }
});

delete finalScoreDist.fb;
delete finalScoreDist.instagram;
delete finalScoreDist.privacyPolicy;

fs.writeFileSync(
  "data/unfilteredScoreDist.json",
  JSON.stringify(finalScoreDist)
);
