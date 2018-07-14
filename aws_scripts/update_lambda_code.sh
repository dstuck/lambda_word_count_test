#!/bin/bash
pushd ..
./make_deploy_zip.sh

function_name="read-file-test"
deploy_bucket="test-bucket-1-dstuck"
deploy_key="lambda_deploys/word_count_lambda.zip"

aws s3 cp word_count_lambda.zip s3://$deploy_bucket/$deploy_key
aws lambda update-function-code \
    --function-name $function_name \
    --s3-bucket $deploy_bucket \
    --s3-key $deploy_key
aws lambda update-function-configuration \
    --function-name $function_name \
    --handler word_count_lambda.lambda_handler \
    --timeout 300
popd

