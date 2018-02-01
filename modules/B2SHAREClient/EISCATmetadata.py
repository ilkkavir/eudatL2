### Create a JSON patch of community metadata.

## args:  ResID, ExpName, Antenna, Resource, DBStartTime, DBStopTime, Location, InfoPath, outPath]

## Metadata schema
# {
#     "community": "b344f92a-cd0e-4e4c-aa09-28b5f95f7e41", 
#     "titles": [
#         {
#             "title": "%title%"
#         }
#     ],
#     "creators": [
#         {
#             "creator_name": "EISCAT Scientific Association"
#         }
#     ],
#     "contributors": [
# 	{
#             "contributor_name": "%Name%", 
#             "contributor_type": "ContactPerson"
# 	}
#     ], 
#     "contact_email": "email",
#     "descriptions": [
#         {
#             "description": "%description%", 
#             "description_type": "Abstract"
#         }
#     ], 
#     "license": {
#         "license": "EISCAT Rules of the Road", 
# 	"license_uri": "https://www.eiscat.se/scientist/data/#rules"  
#     }, 
#     "open_access": false,
#     "embargo_date": "%date%",
#     "disciplines": [
#         "3.4.12 \u2192 Physics \u2192 Geophysics", 
#         "3.5 \u2192 Natural sciences \u2192 Space sciences"
#     ],
#     "keywords": [
#         "Radar", 
#         "Incoherent scatter", 
#         "Ionosphere"
#     ],
#     "resource_types": [
# 	{
#             "resource_type": "EISCAT Level 3 data", 
#             "resource_type_general": "Dataset"
# 	},
# 	{
#             "resource_type": "EISCAT Level 2 data", 
#             "resource_type_general": "Collection"
# 	}
#     ], 
#     "alternate_identifiers": [
#         {
#             "alternate_identifier": "%url%", 
#             "alternate_identifier_type": "URL"
#         }
#     ],
#     "community_specific": {
#         "cee77dd0-9149-4a7b-9c28-85a8f7052bd9": {
# 	    "start_time": "%start_time%", 
#             "end_time": "%end_time%", 
#             "account": [
#                 "%ac%"
#             ],
# 	    "account_info": "%accountSpecs%",
#             "antenna": [
#                 "%ant%"
#             ],
#             "experiment_id": "%eid%", 
#             "experiment_pi": "%name%",
# 	    "info_directory_url": "%url%",
#             "latitude": "%lat%", 
#             "longitude": "%long%", 
#             "parameters": [
#                 "%par%"
#             ],
# 	    "parameter_errors": [
#                 "%Dpar%" 
#             ], 	    
# 	    "version": "%version%"
# 	} 
#     }
# }
# 

class MetaDataPatch():

    
    def __init__(self, args, community_specific_id):

        from jsonpatch import JsonPatch
        from B2fileroutines import dspname

        ## EISCAT metadata from args
        expid=args[0]
        expname = dspname(args[1]).dsp()
        expver =  dspname(args[1]).ver()
        antenna = args[2]
        resource = args[3]

        # FIXME: create embargo date, endTime + three years
        startTime = args[4]
        endTime = args[5]
        
        location = args[6]
        infoPath = args[7]
        fileloc=args[8]

        ## Build the patch
        json_patch_list=[]

        ## Common metadata
        json_patch={"op": "add", "path": "/titles/title", "value": expname + " " + antenna + " " + startTime }
        json_patch_list.append(json_patch)

        json_patch={"op": "add", "path": "/creators/creator_name", "value": "EISCAT Scientific Association" }
        json_patch_list.append(json_patch)

        json_patch={"op": "add", "path": "/license/license", "value": "EISCAT Rules of the Road" }
        json_patch_list.append(json_patch)

        json_patch={"op": "add", "path": "/license/license_uri", "value": "https://www.eiscat.se/scientist/data/#rules" }
        json_patch_list.append(json_patch)

        # FIXME: read from config
        json_patch={"op": "add", "path": "/contact_email", "value": "carl-fredrik.enell@eiscat.se" }
        json_patch_list.append(json_patch)
 
        json_patch={"op": "add", "path": "/descriptions/description", "value": expname + " Level 2 data from EISCAT " + antenna }
        json_patch_list.append(json_patch)

        json_patch={"op": "add", "path": "/descriptions/description_type", "value": "Abstract" }
        json_patch_list.append(json_patch)

        json_patch={"op": "add", "path": "/open_access", "value": False }
        json_patch_list.append(json_patch)

        json_patch={"op": "add", "path": "/embargo_date", "value": endTime } # Fixme!
        json_patch_list.append(json_patch)

        json_patch={"op": "add", "path": "/disciplines", "value": [ "3.4.12 \u2192 Physics \u2192 Geophysics", "3.5 \u2192 Natural sciences \u2192 Space sciences" ] }
        json_patch_list.append(json_patch)

        json_patch={"op": "add", "path": "/keywords", "value": [ "Radar", "Incoherent scatter", "Ionosphere" ] }
        json_patch_list.append(json_patch)

        json_patch={"op": "add", "path": "/resource_types/resource_type", "value": "EISCAT Level 2 data"}
        json_patch_list.append(json_patch)

        json_patch={"op": "add", "path": "/resource_types/resource_type_general", "value": "Collection"}
        json_patch_list.append(json_patch)

        # FIXME get from config and output file name
        json_patch={"op": "add", "path": "/alternate_identifiers/alternate_identifier", "value": "http://foo.bar.baz"}
        json_patch_list.append(json_patch)

        json_patch={"op": "add", "path": "/alternate_identifiers/alternate_identifier_type", "value": "URL" }
        json_patch_list.append(json_patch)

        ## Community-specific metadata         
        json_patch={"op": "add", "path": "/community_specific/" + community_specific_id + "/experiment_id" , "value": expid }
        json_patch_list.append(json_patch)

        
        json_patch={"op": "add", "path": "/community_specific/" + community_specific_id + "/start_time" , "value": startTime }
        json_patch_list.append(json_patch)
                
        json_patch={"op": "add", "path": "/community_specific/" + community_specific_id + "/end_time" , "value": endTime }
        json_patch_list.append(json_patch)

        # Fixme
        json_patch={"op": "add", "path": "/community_specific/" + community_specific_id + "/account" , "value": resource }
        json_patch_list.append(json_patch)

        json_patch={"op": "add", "path": "/community_specific/" + community_specific_id + "/account_info" , "value": resource }
        json_patch_list.append(json_patch)

        # Fixme; multiple antennas?
        json_patch={"op": "add", "path": "/community_specific/" + community_specific_id + "/antenna" , "value": [ antenna ] }
        json_patch_list.append(json_patch)

        json_patch={"op": "add", "path": "/community_specific/" + community_specific_id + "/latitude" , "value":  lat }
        json_patch_list.append(json_patch)

        json_patch={"op": "add", "path": "/community_specific/" + community_specific_id + "/longitude" , "value": long }
        json_patch_list.append(json_patch)
        
        
        json_patch={"op": "add", "path": "/community_specific/" + community_specific_id + "/info_directory_url" , "value": infoPath }
        json_patch_list.append(json_patch)

        json_patch={"op": "add", "path": "/community_specific/" + community_specific_id + "/version" , "value": expver  }
        json_patch_list.append(json_patch)

        json_patch={"op": "add", "path": "/community_specific/" + community_specific_id + "/parameters" , "value": [ "LagProfile", "RawPower" ] }
        json_patch_list.append(json_patch)

        ## Ready.
        return JsonPatch(json_patch_list).to_string()
