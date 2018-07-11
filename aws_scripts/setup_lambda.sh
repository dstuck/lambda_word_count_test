#!/bin/bash

function_name="read-file-test"

vpc="${TEST_VPC_ID:-$(aws ec2 describe-vpcs | jq '.Vpcs[0].VpcId')}"
# echo $vpc

subnets=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$vpc" | jq -r '.Subnets[].SubnetId')

security_group="${TEST_SECURITY_GROUP:-$(aws ec2 describe-security-groups | jq '.SecurityGroups[] | select (.GroupName | contains("default")) | .GroupId')}"

aws lambda update-function-configuration \
--function-name $function_name \
--vpc-config SubnetIds=$(echo $subnets | tr ' ' ,),SecurityGroupIds=$security_group
