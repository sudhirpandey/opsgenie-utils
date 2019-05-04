#! /home/vagrant/Python3/bin/python
import requests
import sys
import json
import time
import os

access_token = os.environ.get('ACCESS_TOKEN', None)
api_server = "https://api.opsgenie.com"

    
def requestWrapper(func, **kwargs):
    attempt=1
    max_attempt=10
    headers = {'Authorization': 'GenieKey ' + access_token, 'Content-Type': 'application/json'}
    url=api_server
    params=None
    data=None
    for key, val in kwargs.items():
        if key == "endpoint":
            url+=val
        if key == "data":
            data=json.dumps(val)
        if key == "params":
            params=val
    response=func(url,headers=headers, params=params,data=data)
    while response.status_code == 429 and attempt <= max_attempt:
        sleep_time_secs=attempt*0.5
        time.sleep(sleep_time_secs)
        attempt+=1
        response = func(url,headers=headers, params=params,data=data)
    return response
    

def getResource(endpoint,params={}):
    response=requestWrapper(requests.get,endpoint=endpoint,params=params)
    return response

def patchResource(endpoint,payload,params={}):
    response=requestWrapper(requests.patch,endpoint=endpoint, data=payload, params=params)
    return response


def deleteResource(endpoint,params={}):
    response=requestWrapper(requests.delete,endpoint=endpoint, params=params)
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



def deleteUser(user_name):
    endpoint='/v2/users/'+user_name
    response=deleteResource(endpoint)
    if response.status_code == 200:
       print("User "+user_name+" deleted")


#returns a list of teamnames
def getTeams():
    endpoint="/v2/teams"
    teams=getResource(endpoint)
    team_names=[]
    #json struct in https://docs.opsgenie.com/docs/team-api#section-list-teams
    for item in (teams.json())['data']:
        team_names.append(str(item['name']))
    return team_names


#check if the user is member of given team
def checkMembership(team_name,username):
    endpoint="/v2/teams/"+team_name
    params={ 'identifierType': 'name' }
    response=getResource(endpoint,params)
    
    #json struct doc on https://docs.opsgenie.com/docs/team-api#section-get-team
    #print(json.dumps(teamMembers.json(), indent=4, separators=(',', ': ')))
    teamMembers=response.json()
    if "members" in teamMembers['data']:    
        for item in teamMembers['data']['members']:
            if item['user']['username'] == username:
               return True
    return False


#remove User from the team
def removeUserFromTeam(team_name, user_name):
    endpoint="/v2/teams/"+team_name+"/members/"+user_name
    params={'teamIdentifierType': 'name'}
    response=deleteResource(endpoint,params)
    if response.status_code == 200:
        print("User "+user_name+"deleted from team "+ team_name)
        return True
    else:
        return False
    


#Wrapper function that checks membership and deletes it if it finds one
def checkAndRemoveUserFromTeam(user_name):
    teams=getTeams()
    for team_name in teams:
        if checkMembership(team_name,user_name):
            if not removeUserFromTeam(team_name,user_name):
                return False
    return True


#remove user from the schedule rotation
def removeUserFromScheduleRotation(schedule_name,rotation_id,user_name,rotation):
    print("User "+ user_name+" found at "+schedule_name+" on Rotation "+ rotation['name'])
    post_data={}
    endpoint="/v2/schedules/"+schedule_name+"/rotations/"+rotation_id
    params={"scheduleIdentifierType": "name"}
    
    post_data['participants']=[]
    for item in rotation['participants']:
        if item['type'] == "user" and item['username'] != user_name:
            post_data['participants'].append(item)

    if len(post_data['participants']) == 0:
       print ("User "+ user_name+" on "+schedule_name+" on Rotation "+ rotation['name'] +"could not be removed as rotation needs at least one member")
       return False

    response=patchResource(endpoint,post_data,params)
    #print(json.dumps(response.json(), indent=4, separators=(',', ': ')))
    if response.status_code == 200:
       return True
    else:
       print(json.dumps(response.json(), indent=4, separators=(',', ': ')))
       return False
       

def checkUserOnRotation(schedule_name, user_name):
    endpoint="/v2/schedules/"+schedule_name+"/rotations"
    params={"scheduleIdentifierType": "name"}
    response=getResource(endpoint,params)
    rotations=response.json()     
    #print(json.dumps(rotations, indent=4, separators=(',', ': ')))
    for rotation in rotations['data']:
        for item in rotation['participants']:
            if item['type'] == "user" and item['username'] == user_name:
                if not removeUserFromScheduleRotation(schedule_name,rotation['id'],user_name,rotation):
                    return False
    return True



def checkAndRemoveUserFromSchedule(username):
    endpoint="/v2/schedules"
    params={'expand': True }
    response=getResource(endpoint,params)

    #https://docs.opsgenie.com/docs/schedule-api#section-list-schedules
    schedules=response.json() 
    for schedule in schedules['data']:
        if not checkUserOnRotation(schedule['name'], username):
            return False
    return True


def main():
    user_to_be_deleted="iquee6eev8di@pokemail.net"

    if not access_token:
         raise ValueError('You must have "ACCESS_TOKEN" env variable')
    users=getAllUsers()
    print(" Users before deletions:"+ str(users))
    deleted_from_all_schedule = checkAndRemoveUserFromSchedule(user_to_be_deleted)
    deleted_from_all_teams = checkAndRemoveUserFromTeam(user_to_be_deleted) 
    
    if deleted_from_all_schedule and deleted_from_all_teams: 
        deleteUser(user_to_be_deleted)
        
        #Need to delay the query a little bit so that the api responds with right set of data.
        time.sleep(5)
        remaining_users=getAllUsers()
        print(" Users after deletion"+str(remaining_users))
    else:
        print("User could not be deleted because it cannot be removed from some schedule or team")

main()
