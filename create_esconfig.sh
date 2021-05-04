#!/bin/sh
#
# Copyright Amazon.com, Inc. and its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT
#
# Licensed under the MIT License. See the LICENSE accompanying this file
# for the specific language governing permissions and limitations under
# the License.
#

if [ -z "$1" ]
then
    echo "Usage: $0 <bucket_name>"
    exit 1
fi
pip3 install --user virtualenv
virtualenv -p python3.7 venv
source ./venv/bin/activate
pip3 install -U requests requests-AWS4Auth cfnresponse
cd $VIRTUAL_ENV/lib/python3.7/site-packages/
rm -rf wheel* easy_install* setuptools* _virtualenv* pip* _distutils* pkg_resources
wget https://aws-waf-operations.s3.amazonaws.com/lambda_function.py
zip -r esconfig.zip .
aws s3 cp esconfig.zip s3://$1
deactivate
cd ../../../..
rm -rf venv build
