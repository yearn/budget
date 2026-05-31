# V3 Protocol Team

## Scope

Funding for the continued development, testing and deployment of the Yearn V3 system.

For a more detailed description of the vision and end goal of V3, please review the [V3 Pitch](https://hackmd.io/@flashfish0x/Bk07G0e6o).

Most of the initial development of the base vault and strategy contracts has been now been completed. Future work for V3 will now be predominantly focused on the development of periphery contracts, live network testing, integration with other Yearn teams, documentation, strategy development as well as continued iteration on the core vault and strategy contracts. 

NOTE: This budget request does not include costs associated with tasks that will be primarily done post prod launch such as bounties, marketing etc.

#### Components:

| **Category** 	|        **Includes**        	|
|:-----------:	|:------------------------:	|
|    **Vault Core**   	|     VaultV3.vy, VaultFactory.vy     	|
|    **Strategy Core**   	| BaseStrategy.sol, BaseLibrary.sol, DiamondHelper.sol 	|
|    **Periphery Contracts**   	|         Generic Acountant, Queue Manager, Registry, Router, Generic Triggers, Debt Allocator, Junior Tranche, Strategy heplers         	| 
|    **Documentation**   	|      API reference guide, Spechs, Integration guides.   |
| **Yearn Integration** | Frontend, yDaemon
|    **Strategy Development**   	| Ape and Foundry strategy mixes. Example strategies, development guides.     	|



## Status

- The [Vault core](https://github.com/yearn/yearn-vaults-v3) is ready for audit that should be starting in April.
- The [Strategy Core](https://github.com/Schlagonia/yearn-base-strategy) is in its final stages of development and should also be ready for an external audit in April.
- Preliminary work has been started on other periphery contracts including a Router, debt Allocator as well as strategy mixes to allow people to start building V3 strategies now.

### Plan

While audits are completed on the core contracts focus will be put on development of the remainder of the stack inlcuding all periphery contracts, Yearn system integration, documentation, strategy development, partner integrations and live network testing.

Preliminary ape.tax deployments will be focused on chains that Yearn does not currently have a presence on to immediatly grow our current addressable market.

For an up to date view of the inteded roadmap please see [V3 Roadmap to Prod](https://hackmd.io/@D4Z1faeARKedWmEygMxDBA/HkPCOm3as).

## Goals
- Complete strategy mixes for both Ape and Foundry.
- Deploy Ape.tax version begining of April.
- Have all periphery contracts developed by end of April.
- Schedule second external audit for both Vault core and Strategy Core
- Ready for Prod deployment by the end of Q2.

### Deadline

2023-07-01

### People

Team Lead: Schlag

Yearn Contributors:
-    FP
-    Wavey

Non-Yearn Contributors:
- Jmonteer

### Money

### General

| **Category** 	|        **Encompases**        	| **Total** |
|:-----------:	|:------------------------:	|:------------------------:	|
|    **Audits**   	| One external audit for both Vault Core and Strategy Core at $20k a piece. | $40k DAI |
|    **Testing**   	| Funds used for deployments and funding for live ape.tax testing of vaults and strategies. 	|$20k DAI |
|    **Totals**   	| n/a | $60K DAI|

Any funds not spent at the end of the period will be transferred back to the yBudget team or considered for the next period.

NOTE: Testing funds will primarily used for funding live strategies. So almost all funds should be available to roll over into any future budget requests. And returned to yBudget once testing is completed.

### Pay
NOTE: Pay is predominately Base pay this request since we have not launched. But will transition more into a performance based incentive structure post launch.
|    **Totals**   	| $35k DAI + 1.5 YFI   	|1 YFI equivalant | n/a | $95    k DAI + 5.5 YFI|


### MAX TOTAL: $155k DAI && 5.5 YFI.
Addresses for each contributors streams TBD.

Auditing and testing funds should be sent to team multi-sig. This will also be the multi-sig to accept any veYFI for performance bonuses or revenue share.
#### V3 team multisig: TBD

### Amount

$155k DAI. 5.5 YFI

### Wallet address

0x3333333368A1ed686392C1534e747F3e15CA286C

### Reporting

Monthly
