import requesthandler
import json


#returns all the users in opsgeine
def getAllUsers():
    endpoint="/v2/users"
    users=requesthandler.getResource(endpoint)
    all_users=[]
    for item in (users.json())['data']:
        all_users.append(str(item['username']))
    return all_users
    #print(json.dumps(users.json(), indent=4, separators=(',', ': ')))



def deleteUser(user_name):
    endpoint='/v2/users/'+user_name
    response=requesthandler.deleteResource(endpoint)
    if response.status_code == 200:
       print("User "+user_name+" deleted")
