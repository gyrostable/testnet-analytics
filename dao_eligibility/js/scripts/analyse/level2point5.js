const fs = require("fs");

const WRITE_FILES = false;

// Completing Arb ---------------------------------------
const registrationEvents = require("../../data/userDataRegistrations.json");

const registrations = registrationEvents.map((e) => e.args[0]);

WRITE_FILES &&
  fs.writeFileSync(
    "analysis/dataRegistrations.json",
    JSON.stringify(registrations)
  );
