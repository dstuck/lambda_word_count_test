#!/bin/sh
pushd zip_links
ln -s ../lib/* .
ln -s ../source/* .
rm __pycache__
zip -r ../word_count_lambda.zip *
popd
