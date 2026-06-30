# Labs

Hands-on exercises, one per module. The concepts in the module READMEs only stick once you've built and broken something. Each lab is self-contained with its own setup/teardown so you never leave billable resources running by accident.

> 💰 **Before any lab:** complete `00-account-setup` — it sets a budget alarm and a least-privilege IAM user. Never run labs as the root account.

| Lab | Module | What you'll build |
|---|---|---|
| 00-account-setup | 00 | Budget alarm, IAM user, AWS CLI configured safely |
| _(more added as modules are built to full depth)_ | | |

Each lab folder will contain: a `README.md` with steps, any IaC (CloudFormation/Terraform) or scripts, and a **teardown** step. Treat teardown as mandatory.
