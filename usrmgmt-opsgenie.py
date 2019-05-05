#! /home/vagrant/Python3/bin/python
import time
import json
import requesthandler
import users as UserAPI
import teams as TeamAPI
import schedule as ScheduleAPI


def main():
    user_to_be_deleted="iquee6eev8di@pokemail.net"
    actOnUser(user_to_be_deleted)

def actOnUser(user_name):
    message=None
    users=UserAPI.getAllUsers()
    #print("Users before deletions:"+ str(users))
    
    if user_name in users:
        deleted_from_all_schedule, message_from_schedule = ScheduleAPI.checkAndRemoveUserFromSchedule(user_name)
        if deleted_from_all_schedule:
            deleted_from_all_teams, message_from_teams = TeamAPI.checkAndRemoveUserFromTeam(user_name)
            if deleted_from_all_teams: 
                success, msg = UserAPI.deleteUser(user_name)
                if success:
                    return (msg, 200)
                else:
                    return (msg, 400)
            else:
                return (message_from_teams, 400)
        else:
            return (message_from_schedule, 400)
    else:
        message="User "+user_name+" was not found"
        print(message)
        return (message, 200)


def lambda_handler(event, context):
    try:
      payload=json.loads(event['body'])
      message, code = actOnUser(payload['username'])
      return requesthandler.response({'message': message}, code)
    except Exception as e:
        if hasattr(e, 'message'):
           return requesthandler.response({'message': e.message}, 400)
        else:
           print(e)
           return requesthandler.response({'message': "Internal Error, please check logs"}, 400)

#main()
