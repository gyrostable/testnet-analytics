const ethers = require("ethers");
const sybilCheckABI = require("../../abis/SybilCheck.json");
const wallet = require("../../utils/wallet");
const sybilCheckAddress = "0x0416BF4141f731C0Ce217C0A0a95C39224d84817";

const scrapeEvent = require("../../utils/scrapeEvent");

const SybilCheck = new ethers.Contract(
  sybilCheckAddress,
  sybilCheckABI,
  wallet
);

const filter = SybilCheck.filters.CheckCompleted(null, null);

scrapeEvent(SybilCheck, filter, 28614813, 31257010, "data/sybilChecks.json");
