const ethers = require("ethers");
const identificationABI = require("../../abis/Indentification.json");
const wallet = require("../../utils/wallet");

const scrapeEvent = require("../../utils/scrapeEvent");

const Identification = new ethers.Contract(
  "0x028437cF5dB90B367e392Ee971639824684D8295",
  identificationABI,
  wallet
);

const filter = Identification.filters.Registration(null);

scrapeEvent(
  Identification,
  filter,
  25786551,
  29702164,
  "data/userDataRegistrations.json"
);
