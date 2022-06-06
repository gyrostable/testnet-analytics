const ethers = require("ethers");
const arbStatuABI = require("../../abis/ArbitrageStatus.json");
const wallet = require("../../utils/wallet");

const scrapeEvent = require("../../utils/scrapeEvent");

const ArbitrageStatus = new ethers.Contract(
  "0x4Ac61ff8EEca99d67f434e60dacf638F546E4cBD",
  arbStatuABI,
  wallet
);

const arbFilter = ArbitrageStatus.filters.LevelCompleted(null);

// scrapeEvent(
//   ArbitrageStatus,
//   arbFilter,
//   24547202,
//   29058463,
//   "data/arbComplete.json"
// );

// Buying NFTs ----------------------------------------
const gyroStoreAddress = "0xe870dbF309100C3f6ab765A5c0B25bec01B6B320";
const gyroStoreABI = require("../../abis/GyroStore.json");

const GyroStore = new ethers.Contract(gyroStoreAddress, gyroStoreABI, wallet);

const nftFilter = GyroStore.filters.BuyGyroNFT(null, null);

scrapeEvent(GyroStore, nftFilter, 24483722, 29058849, "data/nftBought.json");
