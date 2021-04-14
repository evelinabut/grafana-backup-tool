import json
from grafana_backup.dashboardApi import create_folder, create_folder_permissions, get_user_id


def main(args, settings, file_path):
    grafana_url = settings.get('GRAFANA_URL')
    http_get_headers_basic_auth = settings.get('HTTP_GET_HEADERS_BASIC_AUTH')      
    http_post_headers = settings.get('HTTP_POST_HEADERS')
    verify_ssl = settings.get('VERIFY_SSL')
    client_cert = settings.get('CLIENT_CERT')
    debug = settings.get('DEBUG')

    with open(file_path, 'r') as f:
        data = f.read()
        if "permission" in f.name:
          set_perm = 1
        else:
          set_perm = 0

    folder = json.loads(data)
   
    permissions={}
    items=[]
    if set_perm:       
       for i in range(len(folder)):                                            
            for key in folder[i]:               
                if key=="role" :
                    items.append( { key: folder[i][key], "permission": folder[i]["permission"]  })
                if  key=="userId" and folder[i][key]!=0:                                                     
                   result = get_user_id( folder[i]['userLogin'],  grafana_url, http_get_headers_basic_auth, verify_ssl, client_cert, debug)
                   if result[0] == 200:
                        items.append( { key: result[1]["id"], "permission": folder[i]["permission"]  })
                if key=="teamId" and folder[i]["teamId"]!=0:
                   items.append( { key: folder[i][key], "permission": folder[i]["permission"]  })
               
       permissions ={ "items" : items }                
       result = create_folder_permissions( folder[0]['uid'], json.dumps(permissions), grafana_url, http_post_headers, verify_ssl, client_cert, debug)
       print("create permission  folder {0}, status: {1}, msg: {2}".format(folder[i].get('title', ''), result[0], result[1]))
    else:    
       result = create_folder(json.dumps(folder), grafana_url, http_post_headers, verify_ssl, client_cert, debug)
       print("create folder {0}, status: {1}, msg: {2}".format(folder.get('title', ''), result[0], result[1]))
