Sample for running a lambda to read txt files dropped into a lambda and write out word_counts to a db in rds

Several systems were set up using the aws console rather than scripts which makes this project difficult to practically reproduce:
- an s3 bucket
- security groups
- a lambda function
- the lambda function role
- the mysql table was configured in MySQLWorkbench

Requirements:
jq
- `brew install jq`

Updating lib
- `pip install -r requirements -t lib`

Updating lambda code
- `cd aws_scripts`
- `./update_lambda_code.sh`
