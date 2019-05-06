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



def deleteUser(user_name):
    endpoint='/v2/users/'+user_name
    response=requesthandler.deleteResource(endpoint)
    if response.status_code == 200:
        message = "User "+user_name+" deleted"
        print(message)
        return (True,message)
    else:
        print(json.dumps(response.json(), indent=4, separators=(',', ': ')))
        message="Error while deleting user "+user_name
        return (False,message)

