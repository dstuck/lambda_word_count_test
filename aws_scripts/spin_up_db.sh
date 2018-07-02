#!/bin/sh
aws rds create-db-instance \
    --db-subnet-group-name default \
    --db-instance-identifier test-mysql \
    --db-instance-class db.t2.micro \
    --engine MySQL \
    --allocated-storage 10 \
    --db-name word_counts \
    --master-username dstuck \
    --master-user-password $DB_PASSWORD \
    --vpc-security-group-ids sg-0be0c18cf3b3108c0
