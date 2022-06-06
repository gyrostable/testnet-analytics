const fs = require("fs");
const ethers = require("ethers");
const sybilChecksEvents = require("../../data/sybilChecks.json");
const findScores = require("../../utils/findScores");

const eventNames = [
  ...new Set(
    sybilChecksEvents.map((event) =>
      ethers.utils.parseBytes32String(event.args[0])
    )
  ),
];

const inPersonPOAPData = findScores(sybilChecksEvents, "poap");
const sybilListData = findScores(sybilChecksEvents, "sybilList");
const govVotersData = findScores(sybilChecksEvents, "govVoters");
const additionalPOAPsData = findScores(sybilChecksEvents, "additionalPOAPs");
const discordChallengeData = findScores(
  sybilChecksEvents,
  "discord-challenge-1"
);

const userAccountGithubData = findScores(sybilChecksEvents, "github");

findScores(sybilChecksEvents, "github-standardised").forEach((score) => {
  if (userAccountGithubData.find(({ address }) => address === score.address))
    return;
  userAccountGithubData.push(score);
});

const userAccountTwitterData = findScores(sybilChecksEvents, "twitter");
findScores(sybilChecksEvents, "twitter-standardised").forEach((score) => {
  if (userAccountTwitterData.find(({ address }) => address === score.address))
    return;
  userAccountTwitterData.push(score);
});

const userAccountPhoneData = findScores(sybilChecksEvents, "phone");

const moreOAuthsStackOvFlData = findScores(sybilChecksEvents, "stackOvFl");
const moreOAuthsGithubData = findScores(sybilChecksEvents, "githubFollowers");
const moreOAuthsTwitterData = findScores(sybilChecksEvents, "twitterFollowers");
const moreOAuthsRedditData = findScores(sybilChecksEvents, "reddit");
const moreOAuthsMinecraftData = findScores(sybilChecksEvents, "minecraft");

const goldfinchData = findScores(sybilChecksEvents, "goldfinchKYC");
const defiWhitelistData = findScores(sybilChecksEvents, "megaWhitelist");
const coinbaseData = findScores(sybilChecksEvents, "coinbase");
const discordData = findScores(sybilChecksEvents, "discord");

const allData = {
  inPersonPOAPData,
  sybilListData,
  govVotersData,
  additionalPOAPsData,
  discordChallengeData,
  userAccountGithubData,
  userAccountTwitterData,
  userAccountPhoneData,
  moreOAuthsStackOvFlData,
  moreOAuthsGithubData,
  moreOAuthsTwitterData,
  moreOAuthsRedditData,
  moreOAuthsMinecraftData,
  goldfinchData,
  defiWhitelistData,
  coinbaseData,
  discordData,
};

// Filter addresses:
const minters = require("../../analysis/mintAddresses.json");
const poolJoiners = require("../../analysis/poolJoiners.json");
const arbers = require("../../analysis/arbCompleteAddresses.json");
const nftBuyers = require("../../analysis/nftBoughtAddresses.json");
const dataRegisters = require("../../analysis/dataRegistrations.json");
const proposal1Voters = require("../../analysis/snapshot1Voters.json");
const proposal2Voters = require("../../analysis/snapshot2Voters.json");

// Whitelist
const addressesWhichParticipatedInLevels = [
  ...new Set([
    ...minters,
    ...poolJoiners,
    ...arbers,
    ...nftBuyers,
    ...dataRegisters,
    ...proposal1Voters,
    ...proposal2Voters,
  ]),
];

const whiteListMap = {};

addressesWhichParticipatedInLevels.forEach(
  (address) => (whiteListMap[address] = address)
);

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

let removed = 0;
// Remove Black list addresses
for (let [key, value] of Object.entries(allData)) {
  const filteredValue = value.filter(({ address }) => {
    return !BLACK_LIST_ADDRESSES.some(
      (blacklistAddress) =>
        ethers.utils.getAddress(blacklistAddress) ===
        ethers.utils.getAddress(address)
    );
  });
  allData[key] = filteredValue;
  removed += value.length - filteredValue.length;
}

console.log("Blacklist addresses removed:", removed);

// Remove non-white list addresses
for (let [key, value] of Object.entries(allData)) {
  const filteredValue = value.filter(({ address }) => {
    return whiteListMap[address];
  });
  allData[key] = filteredValue;
  removed += value.length - filteredValue.length;
}

console.log("Total addresses removed:", removed);

// for (let key of Object.keys(allData)) {
//   const filePath = `analysis/${key}.json`;
//   const json = JSON.stringify(allData[key]);

//   fs.writeFileSync(filePath, json);
// }

function decodeArray(encoded) {
  const value1 = Math.floor(encoded / 1000000);
  const value2 = Math.floor((encoded % 1000000) / 1000);
  const value3 = encoded % 1000;

  return [value1, value2, value3];
}

const communityCallsData = allData["additionalPOAPsData"]
  .map(({ address, score }) => ({
    address,
    score: decodeArray(score)[0],
  }))
  .filter(({ score }) => Number(score));

const strongAntiSybilData = allData["additionalPOAPsData"]
  .map(({ address, score }) => ({
    address,
    score: decodeArray(score)[1],
  }))
  .filter(({ score }) => Number(score));

const weakAntiSybilData = allData["additionalPOAPsData"]
  .map(({ address, score }) => ({
    address,
    score: decodeArray(score)[2],
  }))
  .filter(({ score }) => Number(score));

delete allData.additionalPOAPsData;

const sybilChallengesData = {
  ...allData,
  communityCallsData,
  strongAntiSybilData,
  weakAntiSybilData,
};

// printRanges(sybilChallengesData);

// // Increment Data as necessary
for (let key of Object.keys(sybilChallengesData)) {
  const range = sybilChallengesData[key].reduce(
    (acc, el) => {
      const newMin = el.score < acc[0] ? +el.score : acc[0];
      const newMax =
        el.score > acc[1] && el.score < 1000000000 ? +el.score : acc[1];
      return [newMin, newMax];
    },
    [Infinity, 0]
  );

  if (key === "moreOAuthsGithubData") {
    sybilChallengesData[key] = sybilChallengesData[key].map((datum) => ({
      ...datum,
      score: +datum.score === 0 ? 1 : datum.score,
    }));
  }
  if (key === "moreOAuthsTwitterData") {
    sybilChallengesData[key] = sybilChallengesData[key].map((datum) => ({
      ...datum,
      score: +datum.score === 3 ? 2 : datum.score,
    }));
  }

  console.log(key, range);

  if (range[0] === 0) {
    const incrementedData = sybilChallengesData[key].map(
      ({ address, score }) => ({ address, score: String(+score + 1) })
    );

    sybilChallengesData[key] = incrementedData;
  }
}

// printRanges(sybilChallengesData);

// Score sybil points

const keyToScoreNameMap = {
  inPersonPOAPData: "4.1 In person POAP",
  sybilListData: "4.2 Sybil.org list",
  govVotersData: "4.3 Governance Voters",
  communityCallsData: "4.4.1 Community Calls",
  strongAntiSybilData: "4.4.2 Strong Anti Sybil",
  weakAntiSybilData: "4.4.3 Weak Anti Sybil",
  discordChallengeData: "4.5 Discord Challenge",
  userAccountGithubData: "4.6.1 User Account Github",
  userAccountTwitterData: "4.6.2 User Account Twitter",
  userAccountPhoneData: "4.6.3 User Account Phone",
  moreOAuthsStackOvFlData: "4.7.1 More OAuths Stack Overflow",
  moreOAuthsGithubData: "4.7.2 More OAuths Github",
  moreOAuthsTwitterData: "4.7.3 More OAuths Twitter",
  moreOAuthsRedditData: "4.7.4 More OAuths Reddit",
  moreOAuthsMinecraftData: "4.7.5 More OAuths Minecraft",
  goldfinchData: "4.8.1 Goldfinch KYC",
  defiWhitelistData: "4.8.2 Defi Whitelist",
  coinbaseData: "4.8.3 Coinbase",
  discordData: "4.8.4: Discord",
};

const keys = Object.keys(keyToScoreNameMap);
const participants = findParticipants(sybilChallengesData);

// const sybilScores = participants.map((address, index) => {
//   const scoreData = {};

//   console.log(index, "out of", participants.length);

//   for (let key of keys) {
//     const dataSlice = sybilChallengesData[key];

//     const relevantData = dataSlice.find(
//       (datum) =>
//         ethers.utils.getAddress(datum.address) ===
//         ethers.utils.getAddress(address)
//     );

//     if (!relevantData) {
//       scoreData[keyToScoreNameMap[key]] = "0";
//     } else {
//       scoreData[keyToScoreNameMap[key]] = String(relevantData.score);
//     }
//   }

//   return {
//     address,
//     "Weighted Sybil Score": weightScoreData(scoreData),
//     "Unweighted component scores": scoreData,
//   };
// });

// fs.writeFileSync("analysis/sybilScores.json", JSON.stringify(sybilScores));

function weightScoreData(scoreData) {
  let weightedScore = 0;
  weightedScore += Number(scoreData["4.1 In person POAP"]) * 4;
  weightedScore += Number(scoreData["4.2 Sybil.org list"]) * 3;
  weightedScore += Number(scoreData["4.3 Governance Voters"]) * 2;
  weightedScore += Number(scoreData["4.4.1 Community Calls"]) * 2;
  weightedScore += Number(scoreData["4.4.2 Strong Anti Sybil"]) * 3;
  weightedScore += Number(scoreData["4.4.3 Weak Anti Sybil"]) * 1;
  weightedScore +=
    Number(scoreData["4.5 Discord Challenge"]) === 3
      ? 5
      : Number(scoreData["4.5 Discord Challenge"]) > 0
      ? Number(scoreData["4.5 Discord Challenge"]) + 1
      : 0;
  weightedScore += Number(scoreData["4.6.1 User Account Github"]) * 1;
  weightedScore += Number(scoreData["4.6.2 User Account Twitter"]) * 1;
  weightedScore += Number(scoreData["4.6.3 User Account Phone"]) * 2;
  weightedScore += Number(scoreData["4.7.1 More OAuths Stack Overflow"]) * 3;
  weightedScore += Number(scoreData["4.7.2 More OAuths Github"]) > 0 ? 3 : 0;
  weightedScore += Number(scoreData["4.7.3 More OAuths Twitter"]) > 0 ? 2 : 0;
  weightedScore += Number(scoreData["4.7.4 More OAuths Reddit"]) * 2;
  weightedScore += Number(scoreData["4.7.5 More OAuths Minecraft"]) * 1;
  weightedScore += Number(scoreData["4.8.1 Goldfinch KYC"]) * 5;
  weightedScore += Number(scoreData["4.8.2 Defi Whitelist"]) * 2;
  weightedScore += Number(scoreData["4.8.3 Coinbase"]) * 5;
  weightedScore += Number(scoreData["4.8.4: Discord"]) * 1;

  // Bonus points
  weightedScore += Number(scoreData["4.7.2 More OAuths Github"]) === 2 ? 1 : 0;
  weightedScore += Number(scoreData["4.7.3 More OAuths Twitter"]) === 2 ? 1 : 0;

  return weightedScore;
}

function findParticipants(data) {
  const participants = [];

  Object.keys(data).forEach((key) => {
    const dataSlice = data[key];

    dataSlice.forEach(
      ({ address }) =>
        !participants.includes(address) && participants.push(address)
    );
  });

  console.log("Number of paricipants =", participants.length);

  return participants;
}

function printRanges(sybilChallengesData) {
  const result = {};
  Object.keys(sybilChallengesData).forEach((key) => {
    if (!result[key]) result[key] = {};

    sybilChallengesData[key].forEach(({ score }) => {
      if (!result[key][+score]) result[key][+score] = 0;
      result[key][+score]++;
    });
  });

  console.log(result);
}
