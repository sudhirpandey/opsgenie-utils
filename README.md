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
The Lamda code  be executed is divided up into multiple files, and also depends on `requests` library that is not provided out of the box  within  amazon. Hence we imported the requests library provided from the boto library. Thus we can only now concentrate on our to be provided as zip file. In this solution we use cloudformation native way of building the package and deploying the lamda with latest code

* #### Building the package and uploading the package.
  ```
  aws cloudformation package --template-file cf-lamda.yaml --s3-bucket cf-templates-1ly7p8skrsncw-eu-north-1 --output-template-file template.packaged.yml

  #The bucket name can be any bucket where the latest cold is now updated.
  ```
* #### Deploying the lamda function.
  Now we use the generated template from the above command to do actual deployment (ie create or update the lamda stack). Here we pass on the Token as argument which will be available to lamda function as  environment variable

  ```
  aws cloudformation deploy --template-file /home/vagrant/Devops/template.packaged.yml --stack-name cfdeploy --parameter-overrides Token=fef1e44b-c80c-xxx-xxxxxxxxxx --capabilities CAPABILITY_IAM 

  ```
