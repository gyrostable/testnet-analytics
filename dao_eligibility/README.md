## Overview
Testnet analytics were performed with JavaScript, the results were subsequently verified against the output of an independent Python script. 

Having matching output from two different analyses in two different languages adds significant guarantees that the outcome is in fact correct. To reproduce the testnet results either analysis can be used as a starting point. Please note that all relevant items of the JavaScript code are shared, whereas in Python only the relevant scripts are included, no charts, ABIs or other supplementary information is explicity documented here.

### General structure
Generally speaking the testnet analysis was done in four steps:
(1) Pull testnet data about Level 1, 2, 2.5, and 3
(2) Pull testnet data about Sybil challenges
(3) Clean and analyse data with specified conditions
(4) Verify output against independent script

### Complementary information
For further information about the weights refer to: [link](https://docs.google.com/spreadsheets/d/1ASrQ5f9K_Sc12cX20cRNflFjUgEGfAUebM5IK7YCW48/edit?usp=sharing)

For further information about the eligibility conditions refer to: [link](FORUM POST) <-- to be updated
