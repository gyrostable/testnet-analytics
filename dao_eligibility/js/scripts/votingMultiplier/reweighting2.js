const fs = require("fs");

const WRITE_FILES = false;
const LOG = true;

const VIPS = [
  ["Tuxon", "0xb4aca4d18c3f3ad9bfddd0a0dc8f669d51798dea", 0],
  ["CryptoStarLight", "0xb16a472835b1aba595016c1737defc68185aeba8", 24],
  ["darktu", "0x6CD01362ad97C772467A7BD91E8F415F7B80ecdD", 0],
  ["moshiri", "0x79e3b45f7d022c91bbd81c135489e1bfb08d6b15", 14],
  ["Chim9", "0x75f58030c190bb4288f56100f0ee49b6eeb4a134", 0],
  ["Gleb", "0x9a0965916851cd6582a8a8cdb9a1c2a1614492d6", 11],
  ["LegionXX", "0x8cf63110418fbe7b7a183c5b5083f8a9c72ba317", 0],
  ["Dutchify", "0x55B33C302E2e0bA07Bd6B077F6E196729E6255E5", 0],
  ["*zkmehdi.eth*", "0x5F367BF126FDa56D88BA88a8978D5496c66B3569", 0],
  ["iman_paydar", "0xe4Bb384bE9a52E7C980887449BAe068A27AED98f", 10],
  ["sYnc", "0x3d80F11957DF2593CdB1C5Eb68EBA2Db796d7687", 0],
  ["Pankage", "0xdB86B02928C47CB1c1D231B21732E6C639b28051", 0],
  ["Robot", "0x935914AD4A126647Af35378384D70c741892a5Fa", 0],
  ["mrfti", "0x3722a8b1E2674FbBA7081C84E39A5cE738B8159D", 12],
  ["sodiumstar", "0x3cc04875E98EDf01065a4B27e00bcfeDdb76CBA8", 0],
  ["mozuku", "0x767A60F295AEDd958932088F9Cd6a4951D8739b6", 0],
  ["jj3ib", "0x97b2589F10E12C1258d99e36C178E1a292924b42", 21],
  ["mehdij2030", "0xE1e93F60bF1eE0C83f0AE375223Eb03E814A3AB7", 0],
  ["isoester", "0x38Dd4D1Cf82B0943d1ED300A792900D252e21921", 0],
  ["ErMia", "0x84f734c6c6fe7bb628e0ff04ff0a5776b8d68f9f", 0],
  ["MrRobot", "0x082098d8828057085A0a73f98Ee0B8B28E575838", 9],
  ["!Ray", "0xC0817E26A97Fe6066321123fadE456F96578ee1c", 0],
  ["flamingskin", "0x8cAab82f095d9db31587911067EAa15F79eF8Bcd", 14],
  ["Kakashii", "0x52434b6fF3333BeA0c168284a0395606465b681D", 0],
  ["blockchainlugano", "0x459AC98eBd0364224EB45814f15644563e00Fcf9", 10],
  ["pv._", "0xf67AeF424802700f5a928a2f6B0f0a395cD43320", 0],
  ["emzod", "0xa0C242d40F0eb145BCD37764905bD9284C21FD65", 21],
  ["Amir", "0x1A74d0285a569120AA2836CB2b0fa58038ADB800", 7],
  ["Hypo", "0xcBa504f2c4441EDD3E6ab57A65da413fD4CeeB8D", 3],
  ["Bublin", "0x9521B350E14D84ca466e0EB7aFbFF17756A9d653", 0],
  ["gyroMΞHDI | 👨🏻🚀🐸", "0xad33E61d1AEd04ffF6d1E5e7AA1d42c2e9eCF5aA", 0],
  ["TerraBellus", "0xA9903BDA477b9A57BD795AdFf9922cB98DB65F04", 0],
  ["Auri", "0x548fAC51A7518aD8d7139B199fEc71263340994A", 0],
  ["spotlight", "0xDFE2b668c6D4a3FA785f86cB2c64E54E30c16cb0", 0],
];

const VIP_MAPPING = {};

VIPS.map(([_, address, bonus]) => (VIP_MAPPING[address.toLowerCase()] = bonus));

const filteredSybilScorers = require("../../analysis/filteredSybilScoreJonas.json");
const addressToBlockMapping = require("../../data/addressToBlockMappings.json");

const newWeightedData = filteredSybilScorers.map((scorer) => {
  if (scorer["weighted_sybil_score"] > 3) {
    scorer["ch_1"] = (scorer["ch_1"] / 4) * 20;
    scorer["ch_3"] = (scorer["ch_3"] / 2) * 15;
    scorer["ch_4_weak"] = (scorer["ch_4_weak"] / 1) * 15;
    scorer["ch_4_strong"] = (scorer["ch_4_strong"] / 3) * 15;
    scorer["ch_4_comm"] = (scorer["ch_4_comm"] / 2) * 5;
    scorer["ch_8_goldfinch"] = (scorer["ch_8_goldfinch"] / 5) * 25;
  }

  const scores = Object.values(scorer).slice(
    2,
    Object.values(scorer).length - 1
  );

  const newWeightedScore = scores.reduce((acc, el) => acc + el, 0);

  return {
    ...scorer,
    newWeightedScore,
  };
});

const uniqueNewWeightedData = newWeightedData.filter(
  ({ address }, index, self) =>
    self.findIndex(({ address: _address }) => _address === address) === index
);

const finalScores = uniqueNewWeightedData.map((scorer) => {
  const blockMapping = addressToBlockMapping.find(
    ({ address }) => address === scorer.address.toLowerCase()
  );

  blockBonus = 0;
  if (blockMapping) {
    const earliestBlock = Math.min(
      ...Object.values(
        addressToBlockMapping.find(
          ({ address }) => address === scorer.address.toLowerCase()
        )
      )
        .slice(2)
        .filter((blockNumber) => blockNumber > 1)
    );
    if (earliestBlock <= 25250000) {
      if (scorer.newWeightedScore <= 2) blockBonus = 7;
      if (scorer.newWeightedScore >= 3 && scorer.newWeightedScore <= 5)
        blockBonus = 13;
      if (scorer.newWeightedScore >= 6 && scorer.newWeightedScore <= 10)
        blockBonus = 20;
      if (scorer.newWeightedScore > 10) blockBonus = 25;
    } else if (earliestBlock <= 27000000) {
      if (scorer.newWeightedScore <= 2) blockBonus = 5;
      if (scorer.newWeightedScore >= 3 && scorer.newWeightedScore <= 5)
        blockBonus = 10;
      if (scorer.newWeightedScore >= 6 && scorer.newWeightedScore <= 10)
        blockBonus = 15;
      if (scorer.newWeightedScore > 10) blockBonus = 20;
    }
  }

  const vipBonus = VIP_MAPPING[scorer.address] ?? 0;

  const newTotalScore = scorer.newWeightedScore + blockBonus + vipBonus;

  return {
    ...scorer,
    blockBonus,
    newWeightedScorePlusBlockBonus: scorer.newWeightedScore + blockBonus,
    vipBonus,
    newTotalScore,
  };
});

const freq = {};

filteredSybilScorers.filter(onlyUnique).map((scorer) => {
  const finalTier = determineFinalTier(scorer["weighted_sybil_score"]);
  if (freq[finalTier]) {
    freq[finalTier]++;
  } else {
    freq[finalTier] = 1;
  }
});

LOG && console.log("Frequency before analysis");
LOG && console.log(freq, totalFreq(freq));

const freq2 = {};
newWeightedData.map((scorer) => {
  const finalTier = determineFinalTier(scorer.newWeightedScore);
  if (freq2[finalTier]) {
    freq2[finalTier]++;
  } else {
    freq2[finalTier] = 1;
  }
});

LOG && console.log("Frequency after conditional reweighting");
LOG && console.log(freq2, totalFreq(freq2));

const freq2_1 = {};
uniqueNewWeightedData.map((scorer) => {
  const finalTier = determineFinalTier(scorer.newWeightedScore);
  if (freq2_1[finalTier]) {
    freq2_1[finalTier]++;
  } else {
    freq2_1[finalTier] = 1;
  }
});

LOG && console.log("Frequency after conditional reweighting unique");
LOG && console.log(freq2_1, totalFreq(freq2_1));

const freq3 = {};

finalScores.map((scorer) => {
  const finalTier = determineFinalTier(scorer.newWeightedScorePlusBlockBonus);

  if (freq3[finalTier]) {
    freq3[finalTier]++;
  } else {
    freq3[finalTier] = 1;
  }
});

LOG && console.log("Frequency after early block bonus");
LOG && console.log(freq3, totalFreq(freq3));

const freq4 = {};

finalScores.map((scorer) => {
  const finalTier = determineFinalTier(scorer.newTotalScore);

  if (freq4[finalTier]) {
    freq4[finalTier]++;
  } else {
    freq4[finalTier] = 1;
  }
});

LOG && console.log("Frequency after vip bonus");
LOG && console.log(freq4, totalFreq(freq4));

const filePath = `dao_eligibility/js/analysis/newWeightedData2.json`;
const json = JSON.stringify(finalScores);
WRITE_FILES && fs.writeFileSync(filePath, json);

// Helpers

function determineFinalTier(newTotalScore) {
  const finalTier =
    newTotalScore >= 30
      ? 45
      : newTotalScore >= 25
      ? 30
      : newTotalScore >= 16
      ? 15
      : newTotalScore >= 8
      ? 2
      : newTotalScore >= 1
      ? 1
      : 0;

  return finalTier;
}

function totalFreq(freq) {
  return Object.values(freq).reduce((acc, el) => acc + el, 0);
}

function onlyUnique(value, index, array) {
  return array.indexOf(value) === index;
}
