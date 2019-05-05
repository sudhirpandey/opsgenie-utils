#!/bin/bash

#Add source into the zip file
echo "========> adding the codes into zip file"
find . -name '*.py' -exec basename {} \; |xargs zip -g function.zip

#Upload the code intp s3 bucket
echo "========> Uploading the function.zip to s3 bucket"
aws s3 cp function.zip s3://democode.s3.bucket

#Change the Logical version of lamda so that lamda stack get updated
echo "========> Bump up the logical Version of cf-template for lamda function"
Deployedversion=$(aws lambda list-versions-by-function --function-name lamda-test-OpsgenieLamdaFunc-1W2W93OH2D3MS | jq '.Versions[] | .Version'|grep -v "LATEST" |tr -d '"')
nextVersion=$(( $Deployedversion+1 ))
cp cf-lamda.yaml /tmp/cf-lamda.yaml
sed -i "s/LambdaVersion1/LambdaVersion${nextVersion}/" /tmp/cf-lamda.yaml
sed -i "s/xxx-xxx-xxx/${ACCESS_TOKEN}/" /tmp/cf-lamda.yaml
sed -i "s/vvv/${nextVersion}/" /tmp/cf-lamda.yaml

#Update the stack
echo "========> Update the lamda Stack"
aws cloudformation update-stack --stack-name lamda-test --template-body file:///tmp/cf-lamda.yaml --capabilities CAPABILITY_IAM
