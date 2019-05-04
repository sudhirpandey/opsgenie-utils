#! /home/vagrant/Python3/bin/python
import requests
import sys
import json
import time
import os

access_token = os.environ.get('ACCESS_TOKEN', None)
api_server = "https://api.opsgenie.com"


def getResource(endpoint,params={}):
    attempt=1
    max_attempt=10
    headers = {'Authorization': 'GenieKey ' + access_token, 'Content-Type': 'application/json'}
    url=api_server+endpoint
    response = requests.get(url, headers=headers, params=params)
    #doc https://docs.opsgenie.com/docs/api-rate-limiting on rate limiting , exponentially grow sleep time up to 5 secs
    while response.status_code == 429 and attempt <= max_attempt:
         sleep_time_secs=attempt*0.5
         time.sleep(sleep_time_secs)
         attempt+=1
         response = requests.get(url, headers=headers, params=params)
    return response

def patchResource(endpoint,payload,params={}):
    attempt=1
    max_attempt=10
    headers = {'Authorization': 'GenieKey ' + access_token, 'Content-Type': 'application/json'}
    url=api_server+endpoint
    response = requests.patch(url,headers=headers, data=json.dumps(payload), params=params)
    while response.status_code == 429 and attempt <= max_attempt:
         sleep_time_secs=attempt*0.5
         time.sleep(sleep_time_secs)
         attempt+=1
         response = requests.patch(url,headers=headers, data=json.dumps(payload), params=params)
    return response
       

#returns all the users in opsgeine
def getAllUsers():
    endpoint="/v2/users"	
    users=getResource(endpoint)
    all_users=[]
    for item in (users.json())['data']:
        all_users.append(str(item['username']))
    return all_users
    #print(json.dumps(users.json(), indent=4, separators=(',', ': ')))




#returns a list of teamnames
def getTeams():
    endpoint="/v2/teams"
    teams=getResource(endpoint)
    team_names=[]
    #json struct in https://docs.opsgenie.com/docs/team-api#section-list-teams
    for item in (teams.json())['data']:
        team_names.append(str(item['name']))
    time.sleep(5)
    return team_names



#returns an users list for a given team
def checkMembership(team_name,username):
    endpoint="/v2/teams/"+team_name
    params={ 'identifierType': 'name' }
    response=getResource(endpoint,params)
    members=[]
    
    #json struct doc on https://docs.opsgenie.com/docs/team-api#section-get-team
    #print(json.dumps(teamMembers.json(), indent=4, separators=(',', ': ')))
    teamMembers=response.json()
    if "members" in teamMembers['data']:    
        for item in teamMembers['data']['members']:
            if item['user']['username'] == username:
               return True
    return False

def removeUserFromScheduleRotation(schedule_name,rotation_id,user_name,rotation):
    print("User "+ user_name+" found at "+schedule_name+" on Rotation "+ rotation['name'])
    #output_dict = [{k:v for k,v in x.items() if k not in ["participants"]} for x in item]
    #print(json.dumps(output_dict, indent=4, separators=(',', ': ')))
    post_data={}
    endpoint="/v2/schedules/"+schedule_name+"/rotations/"+rotation_id
    params={"scheduleIdentifierType": "name"}
    
    post_data['participants']=[]
    for item in rotation['participants']:
        if item['type'] == "user" and item['username'] != user_name:
            post_data['participants'].append(item)

    if len(post_data['participants']) == 0:
       print ("User "+ user_name+" on "+schedule_name+" on Rotation "+ rotation['name'] +"could not be removed as rotation needs at least one member")
       return

    response=patchResource(endpoint,post_data,params)
    print(json.dumps(response.json(), indent=4, separators=(',', ': ')))
       

def checkUserOnRotation(schedule_name, user_name):
    endpoint="/v2/schedules/"+schedule_name+"/rotations"
    params={"scheduleIdentifierType": "name"}
    response=getResource(endpoint,params)
    rotations=response.json()     
    #print(json.dumps(rotations, indent=4, separators=(',', ': ')))
    for rotation in rotations['data']:
        for item in rotation['participants']:
            if item['type'] == "user" and item['username'] == user_name:
                removeUserFromScheduleRotation(schedule_name,rotation['id'],user_name,rotation)
    return False



def checkUserOnSchedule(username):
    endpoint="/v2/schedules"
    params={'expand': True }
    response=getResource(endpoint,params)
    users=[]

    #https://docs.opsgenie.com/docs/schedule-api#section-list-schedules
    schedules=response.json() 
    #if len(schedules['data']['rotations']) > 0:
    for schedule in schedules['data']:
        checkUserOnRotation(schedule['name'], username)


def main():
    user_to_be_deleted="iquee6eev8di@pokemail.net"
    #users=getAllUsers()
    teams=getTeams()
    #users_from_all_schedules=getUsersOnSchedule()
    users_from_all_teams=[]
    
    if not access_token:
         raise ValueError('You must have "ACCESS_TOKEN" env variable')

    for team_name in teams:
        found=checkMembership(team_name,user_to_be_deleted)
        if found:
           print("user found")
        time.sleep(10)
	    #add only unique members form team  in our final team list
        #users_from_all_teams.extend(users)

    checkUserOnSchedule(user_to_be_deleted)
     

main()
