# Description of this solution
This solution is designed to run as lamda function that gets triggred via API gateway.

### Usage
The lamda function gets triggered and does deletion of User if possible from Opsgeine. The endpont of API gateway accepts POST method and expect a json payload

```
curl -H x-api-key:xxx-xxx-xxx -XPOST https://iikbcte807.execute-api.eu-north-1.amazonaws.com/test -d '{ "username":"hari@example.com" }'
```

### API gateway
The API enpoint is configured to  need api-key (For now) in order to be accessible. This will give some kind of of protection as our api end point would not be misused, and helps to have Lamda executed only by request which provides api-key as header.The API gateway end point also has rate limitation. For now this API gateway is provisoned using AWS console. 


### Lamda function
The Lamda code  be executed is divided up into multiple files, and also depends on `requests` library that is not provided out of the box  within  amazon. Hence the approach of creating a deployment Package was taken , where all the code and need dependency is zipped up and uploaded into s3 bucket. The lamda function will then be using this uploaded zip file from s3 as its code.

* #### Building the package.
  The followed doc was https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html.
  ```
  #Create the zip file with dependcies
  cd /home/vagrant/Python3/lib64/python3.4/site-packages/
  zip -r9 ../../../../function.zip .

  #Move the generated function.zip to folder where source code exist and add your python files
  git clone git@github.com:sudhirpandey/opsgenie-utils.git
  mv function-zip opsgenie-utils
  find . -name '*.py' -exec basename {} \; |xargs zip -g function.zip  
  ```
* #### Deploying the lamda function.
  We have two cloudformation templates that would help us to create the desired resource in AWS.
  First we need to create the s3 bucket where the `function.zip` obtained form above would be uploaded.
  ```
  aws cloudformation create-stack --stack-name myteststack --template-body file://cf-bucket.yaml
  ```

  Now we need to upload the file to bucket 
  ```
  aws s3 cp function.zip s3://democode.s3.bucket
  ```
  
  Now that the code is in s3 bucket we can create the lamda function using the cf-lamda.yaml. One thing to notice is cf-lamda.yaml has environment variable `ACCESS_TOKEN`, whose value need to be token obt  ained from opsgeine. Once substitited withe the right token value following aws cli can be executed to deploy the lamda function. 
  ```
  #create stack
  aws cloudformation create-stack --stack-name lamda-test --template-body file://cf-lamda.yaml --capabilities CAPABILITY_IAM

  #Some time we need to update the stack when the new code is uploaded in the s3 bucket
  aws cloudformation create-stack --stack-name lamda-test --template-body file://cf-lamda.yaml --capabilities CAPABILITY_IAM

  ```

# Release Process for development
It was found that once the zip file with updated code was uploaded into s3, lamda deployment was still not updated. Hence we need to create another deployment version it starts to use new code, Hence `releash.sh` can be used to automate the deployment of new code into this setup. With each release launch ,it updates the version of deployment by 1.

