Sample for running a lambda to read txt files dropped into a lambda and write out word_counts to a db in rds

Requirements:
jq
- `brew install jq`

Updating lib
- `pip install -r requirements -t lib`

Updating lambda code
- `cd aws_scripts`
- `./update_lambda_code.sh`
