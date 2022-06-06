const ethers = require("ethers");
const gyroLibABI = require("../../abis/GyroLib.json");
const bPoolABI = require("../../abis/BPool.json");
const scrapeEvent = require("../../utils/scrapeEvent");
const contractAddresses = require("../../contractAddresses.json");

const wallet = require("../../utils/wallet");

// const GyroLib = new ethers.Contract(
//   contractAddresses.networks.kovan.GyroLib,
//   gyroLibABI,
//   wallet
// );

// const mintFilter = GyroLib.filters.Mint(null, null);

// scrapeEvent(GyroLib, mintFilter, 24052769, 31298516, "mintEvents.json");

const BPool = new ethers.Contract(
  contractAddresses.networks.kovan["pool-gyd_usdc"],
  bPoolABI,
  wallet
);

const logJoinFilter = BPool.filters.LOG_JOIN(
  null,
  contractAddresses.networks.kovan.GyroProxy,
  null
);

scrapeEvent(BPool, logJoinFilter, 24054174, 31298269, "data/joinPool.json");
