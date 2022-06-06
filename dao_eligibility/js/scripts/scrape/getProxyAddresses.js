const fs = require("fs");
const ethers = require("ethers");
const proxyRegistryABI = require("../../abis/ProxyRegistry.json");
const minters = require("../../analysis/mintAddresses.json");

const wallet = require("../../utils/wallet");

const proxyRegistry = new ethers.Contract(
  "0x130767E0cf05469CF11Fa3fcf270dfC1f52b9072",
  proxyRegistryABI,
  wallet
);

const startIndex = 34717;
const endIndex = minters.length;
const filePath = "analysis/minterToProxyMap4.json";

(async () => {
  for (let i = startIndex; i < endIndex; i++) {
    console.log(i + 1 + " of " + endIndex);
    const minter = minters[i];
    const proxy = await proxyRegistry.proxies(minter);
    console.log(minter);
    console.log(proxy);
    if (proxy === "0x0000000000000000000000000000000000000000") continue;

    const minterToProxyMap = require("../../" + filePath);
    delete minterToProxyMap.state;

    if (!minterToProxyMap[minter]) {
      console.log("UPDATE!");
      minterToProxyMap[minter] = proxy;
      fs.writeFileSync(
        filePath,
        JSON.stringify({
          state: i + 1 + " of " + endIndex,
          ...minterToProxyMap,
        })
      );
    }
  }
})();

const map1 = require("../../analysis/minterToProxyMap1.json");
const map2 = require("../../analysis/minterToProxyMap2.json");
const map3 = require("../../analysis/minterToProxyMap3.json");
const map4 = require("../../analysis/minterToProxyMap4.json");

const map = { ...map1, ...map2, ...map3, ...map4 };

delete map.state;

fs.writeFileSync("analysis/minterToProxyMap.json", JSON.stringify(map));
