import os
import json
from grafana_backup.dashboardApi import get_all_annotations, search_dashboard_by_id
from grafana_backup.commons import to_python2_and_3_compatible_string, print_horizontal_line, save_json


def main(args, settings):
    backup_dir = settings.get('BACKUP_DIR')
    timestamp = settings.get('TIMESTAMP')
    grafana_url = settings.get('GRAFANA_URL')
    http_get_headers = settings.get('HTTP_GET_HEADERS')
    verify_ssl = settings.get('VERIFY_SSL')
    client_cert = settings.get('CLIENT_CERT')
    debug = settings.get('DEBUG')
    pretty_print = settings.get('PRETTY_PRINT')
    uid_support = settings.get('UID_SUPPORT')

    folder_path = '{0}/{1}/annotations'.format(backup_dir, timestamp)   

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


    get_all_annotations_and_save(grafana_url, http_get_headers, verify_ssl, client_cert, debug, folder_path, pretty_print)
    print_horizontal_line()

def get_all_annotations_and_save(grafana_url, http_get_headers, verify_ssl, client_cert, debug, folder_path, pretty_print):
    (status,content) = get_all_annotations(grafana_url, http_get_headers, verify_ssl, client_cert, debug)

    annotations=content

    if status == 200:
        print("There are {0} annotations:".format(len(annotations)))
        for annotation in annotations:
            print("name: {0}".format(to_python2_and_3_compatible_string(annotation['text'])))
            (status,dashboard) = search_dashboard_by_id(annotation['dashboardId'],grafana_url, http_get_headers, verify_ssl, client_cert, debug)          
            annotation["dashboard_uid"]= dashboard[0]['uid']
            if status == 200:              
               file_name= '{0}_{1}'.format(dashboard[0]['uid'],annotation['id'])
               save_annotation(
                    to_python2_and_3_compatible_string(annotation['id']),
                    file_name,
                    annotation,
                    folder_path,
                    pretty_print
                )        
            else:
                print("get dashboard for annotation failed, status: {0}, msg: {1}".format(status, content))
    else:
        print("get annotations failed, status: {0}, msg: {1}".format(status, content))       


def save_annotation(annotation_text, file_name, content, folder_path, pretty_print):
    file_path = save_json(file_name, content, folder_path, 'annotation', pretty_print)
    print("annotation:{0} is saved to {1}".format(annotation_text, file_path))


