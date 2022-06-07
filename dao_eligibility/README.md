## Overview
Testnet analytics were performed with the attached JavaScript code, the results were subsequently verified against the output of an independent Python script. 

Matching the output of two different analyses in two different languages adds significant guarantees that the final outcome is in fact correct. You may use  either analysis as a starting point to reproduce the testnet results. However, please note that all relevant items of the JS script are shared, whereas in Python only the relevant scripts are included, no charts, ABIs or other supplementary information is explicity documented here.

### General structure
Generally speaking the testnet analysis was done in four steps:
- (1) Pull testnet data about Level 1, 2, 2.5, and 3
- (2) Pull testnet data about Sybil challenges
- (3) Clean and analyse data with specified conditions
- (4) Verify output against independent script

### Complementary information
- For further information about the weights refer to: [link](https://docs.google.com/spreadsheets/d/1ASrQ5f9K_Sc12cX20cRNflFjUgEGfAUebM5IK7YCW48/edit?usp=sharing)
- For further information about the eligibility conditions refer to: [link](FORUM POST) <-- to be updated
