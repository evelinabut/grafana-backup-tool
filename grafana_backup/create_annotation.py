import json
from grafana_backup.dashboardApi import create_annotation, get_dashboard_by_uid


def main(args, settings, file_path):
    grafana_url = settings.get('GRAFANA_URL')
    http_get_headers = settings.get('HTTP_GET_HEADERS')    
    http_post_headers = settings.get('HTTP_POST_HEADERS')
    verify_ssl = settings.get('VERIFY_SSL')
    client_cert = settings.get('CLIENT_CERT')
    debug = settings.get('DEBUG')

    with open(file_path, 'r') as f:
        data = f.read()      

    annotation = json.loads(data)
   
    payload={
     "panelId" : annotation['panelId'],
     "time" : annotation['time'],
     "timeEnd" : annotation['timeEnd'],
     "tags" : annotation['tags'],
     "text" : annotation['text'], 
    }
   
    (status, dashboard) = get_dashboard_by_uid(annotation['dashboard_uid'], grafana_url, http_get_headers, verify_ssl, client_cert, debug)
    if status == 200:
        payload["dashboardId"] = dashboard['dashboard']['id']
        print(payload)      
        result = create_annotation(json.dumps(payload), grafana_url, http_post_headers, verify_ssl, client_cert, debug)
        print("create annotation response status: {0}, msg: {1} \n".format( result[0], result[1]))
    else:
      print("error by getting dashboard uid")
