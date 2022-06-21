## Overview

Testnet analytics were performed with the attached JavaScript code, the results were subsequently verified against the output of an independent Python script. 

Matching the output of two different analyses in two different languages adds significant guarantees that the final outcome is in fact correct. You may use  either analysis as a starting point to reproduce the testnet results. However, please note that all relevant items of the JS script are shared, whereas in Python only the relevant scripts are included, no charts, ABIs or other supplementary information is explicity documented here.

### General structure

Generally speaking the testnet analysis was done in four steps:
- (1) Pull testnet data about Level 1, 2, 2.5, and 3
- (2) Pull testnet data about Sybil challenges
- (3) Clean and analyse data with specified conditions
- (4) Verify output against independent script

### Manual changes

Two manual changes were made that deviate from the results/ methodology of the analysis scripts. Previously obtained Sybil points from the following two addresses were transferred to a new address:

- 0xca16c355D32aAAFAe5DE49E39eBd4c40977A67Ee
- 0x97b2589F10E12C1258d99e36C178E1a292924b42

In both cases the owner requested a change of their testnet address, which was granted after the owner could (a) proof their control over the respective address and (b) provided an exceptionally good explanation for the need to transfer sybil points to a new address.

The contracts are deployed now, as such no further exceptions can be made in any case.

### Complementary information

- For further information about the weights refer to: [link](https://docs.google.com/spreadsheets/d/1ASrQ5f9K_Sc12cX20cRNflFjUgEGfAUebM5IK7YCW48/edit?usp=sharing)
- For further information about the eligibility conditions refer to: [link](https://gov.gyro.finance/t/final-proposal-on-ggwp-2-migrating-founding-members-of-the-gyroscope-dao-from-the-testnet-game-to-the-ethereum-mainnet/12429)
