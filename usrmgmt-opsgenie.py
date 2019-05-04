#! /home/vagrant/Python3/bin/python
import time
import json
import users as UserAPI
import teams as TeamAPI
import schedule as ScheduleAPI


def main():
    user_to_be_deleted="iquee6eev8di@pokemail.net"
    actOnUser(user_to_be_deleted)

def actOnUser(user_name):
    users=UserAPI.getAllUsers()
    print(" Users before deletions:"+ str(users))
    deleted_from_all_schedule = ScheduleAPI.checkAndRemoveUserFromSchedule(user_name)
    deleted_from_all_teams = TeamAPI.checkAndRemoveUserFromTeam(user_name) 
    
    if deleted_from_all_schedule and deleted_from_all_teams: 
        UserAPI.deleteUser(user_name)
        
        #Need to delay the query a little bit so that the api responds with right set of data.
        time.sleep(1)
        remaining_users=UserAPI.getAllUsers()
        message="User deleted Sucessfully"
        print(" Users after deletion"+str(remaining_users))
        return (message, 200)
    else:
        message="User could not be deleted because it cannot be removed from some schedule or team"
        print(message)
        return (message, 400)


def response(message, status_code):
    return {
        'statusCode': str(status_code),
        'body': json.dumps(message),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
            },
        }

def lambda_handler(event, context):
    try:
      payload=json.loads(event['body'])
      message, code = actOnUser(payload['username'])
      return response({'message': message}, code)
    except Exception as e:
        if hasattr(e, 'message'):
           return response({'message': e.message}, 400)
        else:
           print(e)
           return response({'message': "Internal Error, please check logs"}, 400)

main()
