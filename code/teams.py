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
        message = "User "+user_name+" deleted from team "+ team_name
        print(message)
        return (True,message)
    else:
        print(json.dumps(response.json(), indent=4, separators=(',', ': ')))
        message = "User could "+ user_name +"not be removed from team "+team_name+", check Logs for details"
        return (False,message)



#Wrapper function that checks membership and deletes it if it finds one
def checkAndRemoveUserFromTeam(user_name):
    teams=getTeams()
    for team_name in teams:
        if checkMembership(team_name,user_name):
            success, message = removeUserFromTeam(team_name,user_name)
            if not success:
                return (False, message)
    return (True,"User removed from all the teams")
