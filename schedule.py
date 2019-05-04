import json
import requesthandler

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

    response=requesthandler.patchResource(endpoint,post_data,params)
    #print(json.dumps(response.json(), indent=4, separators=(',', ': ')))
    if response.status_code == 200:
       return True
    else:
       print(json.dumps(response.json(), indent=4, separators=(',', ': ')))
       return False


def checkUserOnRotation(schedule_name, user_name):
    endpoint="/v2/schedules/"+schedule_name+"/rotations"
    params={"scheduleIdentifierType": "name"}
    response=requesthandler.getResource(endpoint,params)
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
    response=requesthandler.getResource(endpoint,params)

    #https://docs.opsgenie.com/docs/schedule-api#section-list-schedules
    schedules=response.json()
    for schedule in schedules['data']:
        if not checkUserOnRotation(schedule['name'], username):
            return False
    return True
