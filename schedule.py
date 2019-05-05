import json
import requesthandler

#remove user from the schedule rotation
def removeUserFromScheduleRotation(schedule_name,rotation_id,user_name,rotation):
    print("User "+ user_name+" found at "+schedule_name+" on Rotation "+ rotation['name'])
    post_data={}
    endpoint="/v2/schedules/"+schedule_name+"/rotations/"+rotation_id
    params={"scheduleIdentifierType": "name"}

    #loop through the existing participants and create new list except the user that is to be deleted. 
    post_data['participants']=[]
    for item in rotation['participants']:
        if item['type'] == "user" and item['username'] != user_name:
            post_data['participants'].append(item)

    #if the final result of new list is zero then user that was to be deleted seems to be the only one in rotation, which does not allow us to patch rotation object.
    if len(post_data['participants']) == 0:
       message = "User "+ user_name+" on "+schedule_name+" on Rotation "+ rotation['name'] +"could not be removed as rotation needs at least one member"
       print(message)
       return (False, message)

    response=requesthandler.patchResource(endpoint,post_data,params)
    #print(json.dumps(response.json(), indent=4, separators=(',', ': ')))
    if response.status_code == 200:
       return (True,"Update rotation")
    else:
       print(json.dumps(response.json(), indent=4, separators=(',', ': ')))
       return (False,"Rotation "+rotation['name']+"on schedule "+schedule_name+" could not be updated. More on server logs")


def removeUserFromAllRotations(schedule_name, user_name):
    endpoint="/v2/schedules/"+schedule_name+"/rotations"
    params={"scheduleIdentifierType": "name"}
    response=requesthandler.getResource(endpoint,params)
    rotations=response.json()
    #print(json.dumps(rotations, indent=4, separators=(',', ': ')))
    for rotation in rotations['data']:
        for item in rotation['participants']:
            if item['type'] == "user" and item['username'] == user_name:
                success, message = removeUserFromScheduleRotation(schedule_name,rotation['id'],user_name,rotation)
                if not success:
                    return (False, message)
    return (True,"User deleted from all rotations")



def checkAndRemoveUserFromSchedule(username):
    endpoint="/v2/schedules"
    params={'expand': True }
    response=requesthandler.getResource(endpoint,params)

    #https://docs.opsgenie.com/docs/schedule-api#section-list-schedules
    schedules=response.json()
    for schedule in schedules['data']:
        success, message = removeUserFromAllRotations(schedule['name'], username)
        if not success:
            return (False,message)
    return (True,"User deleted from all schedules")
