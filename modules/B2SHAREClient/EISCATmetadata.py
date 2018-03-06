""" Create JSON objects from metadata.

Inputs: args (packed arguments from subprocess), output file URL, UUIDs
Outputs: JSON objects: basic entry (string), community metadata (JSON Patch object as string)


 draft_json = MetaDataJSON(args, out_file_url, community_uuid, community_specific_id)([ResID, ExpName, Antenna, Resource, DBStartTime, DBStopTime, Location, InfoPath, outPath],
  out_file_url, community_uuid, community_specific_id)
"""

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
def MetaDataJSON(args, out_file_url, community_uuid, community_specific_id):
    
    from B2fileroutines import dspname
    from datetime import timedelta
    import json
    
    ## EISCAT metadata from args
    expid=str(args[0])
    expname = dspname.DSPname(args[1]).dsp()
    expver =  dspname.DSPname(args[1]).ver()
    assoc = dspname.DSPname(args[1]).cc().upper() # Fixme: take multiple entries from resource if exists
    assoc=assoc.replace("GE","DE")
    assoc=assoc.replace("NI","JP")
    assoc=assoc.replace("SW","SE")
    
    antenna = args[2]

    antMap={"uhf":"UHF", "vhf":"VHF", "kir":"KIR", "sod":"SOD", "hf":"HF", "32m":"32m", "32p":"32p", "42m":"42m", "lyr":"ESR" }

    antenna=antMap[antenna]
    
    resource = args[3]
    
    startTime = args[4].strftime('%Y-%m-%dT%H:%M:%S')
    endTime = args[5]
    embargoTime = endTime + timedelta(1096)
    
    endTime = endTime.strftime('%Y-%m-%dT%H:%M:%S')
    embargoTime = embargoTime.strftime('%Y-%m-%dT%H:%M:%S')
    
    infoPath = args[7]
    
    # FIXME: read from somewhere
    stnLat = {'UHF': '69.58', 'VHF': '69.58', 'HF': '69.58', 'KIR': '67.87', 'SOD': '67.37' , '32m': '78.15', '32p': '78.15', '42m': '78.15' }
    stnLong = {'UHF': '19.23', 'VHF': '19.23', 'HF': '19.23', 'KIR': '20.43', 'SOD': '26.63', '32m': '16.02', '32p': '16.02', '42m': '16.02' }
    latitude = stnLat[antenna]
    longitude = stnLong[antenna]
 
    
    ## Build JSON metadata object
    draft_json={}

    # Draft title
    draft_json.update({ "titles": [ { "title": expname + " " + antenna + " " + startTime } ], "community": community_uuid })

    # One Creators entry
    # FIXME: read from config
    draft_json.update({ "creators" : [ {"creator_name": "EISCAT Scientific Association"} ] })

    # License
    # FIXME: read from config
    draft_json.update({ "license": { "license": "EISCAT Rules of the Road", "license_uri": "https://www.eiscat.se/scientist/data/#rules" } })

    # Email address
    # FIXME: read from config
    draft_json.update({ "contact_email": "carl-fredrik.enell@eiscat.se" })

    # Description text
    draft_json.update({ "descriptions": [ {"description": expname + " Level 2 data from EISCAT " + antenna, "description_type": "Abstract" } ] })
                      
    # Embargo
    # FIXME only if in future
    draft_json.update({ "open_access":False, "embargo_date": embargoTime })

    # Disciplines and keywords
    draft_json.update({ "disciplines": [ "3.4.12 \u2192 Physics \u2192 Geophysics", "3.5 \u2192 Natural sciences \u2192 Space sciences"], "keywords": [ "Radar", "Incoherent scatter", "Ionosphere" ] })

    # Type (Level 2)
    draft_json.update({ "resource_types": [ {"resource_type": "EISCAT Level 2 data", "resource_type_general": "Collection"} ] })

    # URLs to data in collection
    # FIXME: allow multiple
    draft_json.update( { "alternate_identifiers": [ { "alternate_identifier": out_file_url, "alternate_identifier_type": "URL" } ] } )

   
    ## Community-specific metadata
    community_json={}
                
    community_json.update({ "experiment_id": expid, "start_time": startTime, "end_time": endTime })

    # FIXME: multiple associates 
    community_json.update({ "account": [ assoc ], "account_info": resource  })

    
    # FIXME: allow multiple antennas
    community_json.update({ "antenna": [ antenna ] })

    # Position
    community_json.update({ "latitude":  latitude, "longitude": longitude })

    
    # Info location
    community_json.update({ "info_directory_url": infoPath })

    # Experiment version
    community_json.update({ "version": expver  })

    # FIXME: check if RawData are available, etc
    community_json.update({ "parameters": [ "LagProfile", "ParameterBlock" ] })

    ## Insert community specific metadata in B2 metadata
    draft_json.update({ "community_specific": { community_specific_id: community_json } })

    ## Return JSON object
    draft_json=json.dumps(draft_json,sort_keys=False)
    return(draft_json)
