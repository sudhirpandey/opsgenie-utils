#!/bin/bash

#Add source into the zip file
echo "========> Package the code and upload code"
aws cloudformation package --template-file cf-lamda.yaml --s3-bucket cf-templates-1ly7p8skrsncw-eu-north-1 --output-template-file template.packaged.yml

#Deploy and update the stack to new code
echo "========> Uploading the stack to use new code"
aws cloudformation deploy --template-file /home/vagrant/Devops/template.packaged.yml --stack-name cfdeploy --parameter-overrides Token=${ACCESS_KEY} --capabilities CAPABILITY_IAM
