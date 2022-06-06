const { ethers, BigNumber } = require("ethers");

const provider = new ethers.providers.InfuraProvider(42, {
  projectId: process.env.INFURA_PROJECT_ID,
  projectSecret: process.env.INFURA_PROJECT_SECRET,
});

const wallet = new ethers.Wallet(process.env.KOVAN_PRIVATE_KEY).connect(
  provider
);

module.exports = wallet;
