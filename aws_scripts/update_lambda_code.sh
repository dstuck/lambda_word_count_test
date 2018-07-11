#!/bin/bash
pushd ..
./make_deploy_zip.sh

function_name="read-file-test"

aws lambda update-function-code \
    --function-name $function_name \
    --zip-file fileb://$PWD/word_count_lambda.zip
aws lambda update-function-configuration \
    --function-name $function_name \
    --handler word_count_lambda.lambda_handler \
    --timeout 60
popd

