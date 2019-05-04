import requesthandler
import json

#returns a list of teamnames
def getTeams():
    endpoint="/v2/teams"
    teams=requesthandler.getResource(endpoint)
    team_names=[]
    #json struct in https://docs.opsgenie.com/docs/team-api#section-list-teams
    for item in (teams.json())['data']:
        team_names.append(str(item['name']))
    return team_names


#check if the user is member of given team
def checkMembership(team_name,username):
    endpoint="/v2/teams/"+team_name
    params={ 'identifierType': 'name' }
    response=requesthandler.getResource(endpoint,params)

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
    response=requesthandler.deleteResource(endpoint,params)
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
