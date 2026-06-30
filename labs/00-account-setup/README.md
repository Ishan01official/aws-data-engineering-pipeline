# Lab 00 · Safe Account Setup

The first thing a professional does in a new AWS account is make it hard to accidentally spend money or get breached. Do this before anything else.

## Steps

1. **Stop using the root user.** The root account email/password is for break-glass only. Create an IAM admin user for daily work, and enable MFA on both.
2. **Set a budget alarm.** AWS Budgets → create a monthly cost budget (e.g. $10) with an email alert at 80%. This is your smoke detector.
3. **Enable MFA** on the root user and your IAM user.
4. **Configure the CLI** with the IAM user's access keys: `aws configure`. Verify with `aws sts get-caller-identity`.
5. **Pick one region and stick to it** for labs (resources in other regions are easy to forget and keep paying for).

## Why this matters

The most common beginner AWS story is a surprise bill from a resource left running in a forgotten region, or a leaked root key. Both are prevented here in ten minutes. → See [Module 01](../../01-aws-core-services/) for the IAM concepts behind this.

## Teardown

Nothing billable is created in this lab (budgets and IAM users are free). Safe to leave as-is.
