#! /home/vagrant/Python3/bin/python
import time
import users as UserAPI
import teams as TeamAPI
import schedule as ScheduleAPI


def main():
    user_to_be_deleted="iquee6eev8di@pokemail.net"

    users=UserAPI.getAllUsers()
    print(" Users before deletions:"+ str(users))
    deleted_from_all_schedule = ScheduleAPI.checkAndRemoveUserFromSchedule(user_to_be_deleted)
    deleted_from_all_teams = TeamAPI.checkAndRemoveUserFromTeam(user_to_be_deleted) 
    
    if deleted_from_all_schedule and deleted_from_all_teams: 
        UserAPI.deleteUser(user_to_be_deleted)
        
        #Need to delay the query a little bit so that the api responds with right set of data.
        time.sleep(1)
        remaining_users=UserAPI.getAllUsers()
        print(" Users after deletion"+str(remaining_users))
    else:
        print("User could not be deleted because it cannot be removed from some schedule or team")

def lambda_handler(event, context):
    main

main()
