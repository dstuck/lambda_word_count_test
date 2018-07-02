#!/bin/bash
pushd ..
./make_deploy_zip.sh
aws lambda update-function-code \
    --function-name read-file-test \
    --zip-file fileb://$PWD/word_count_lambda.zip
aws lambda update-function-configuration \
    --function-name read-file-test \
    --handler word_count_lambda.lambda_handler \
    --timeout 60
popd

