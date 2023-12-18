from grafana_backup.api_checks import main as api_checks
from grafana_backup.save_dashboards import main as save_dashboards
from grafana_backup.save_datasources import main as save_datasources
from grafana_backup.save_folders import main as save_folders
from grafana_backup.save_alert_channels import main as save_alert_channels
from grafana_backup.save_annotations import main as save_annotations
from grafana_backup.archive import main as archive
from grafana_backup.s3_upload import main as s3_upload
from grafana_backup.save_orgs import main as save_orgs
from grafana_backup.save_users import main as save_users
from grafana_backup.azure_storage_upload import main as azure_storage_upload
from git import Repo
import os,sys,shutil


def main(args, settings):
    arg_components = args.get('--components', False)
#    arg_no_archive = args.get('--no-archive', False)

    backup_dir = settings.get('BACKUP_DIR')
    timestamp = settings.get('TIMESTAMP')
    git_user = settings.get('GIT_USER')
    git_token = settings.get('GIT_TOKEN')
    grafana_url = settings.get('GRAFANA_URL')
 
    backup_functions = {'dashboards': save_dashboards,
                     #   'datasources': save_datasources,
                         'folders': save_folders,
                        'alert-channels': save_alert_channels,
                        'annotations': save_annotations,
                        'organizations': save_orgs,
                        'users': save_users}

    (status, json_resp, uid_support, paging_support) = api_checks(settings)

    # Do not continue if API is unavailable or token is not valid
    if not status == 200:
        print("server status is not ok: {0}".format(json_resp))
        sys.exit(1)

    settings.update({'UID_SUPPORT': uid_support})
    settings.update({'PAGING_SUPPORT': paging_support})

    repo_path = "grafana_backups"
    if not os.path.exists("grafana_backups/.git"):
          print('\ncloning https://gitlab.kit.edu/kit/scc/sdm/grafana_backups.git at {0}'.format(repo_path) )
          repo_url= 'https://{0}:{1}@gitlab.kit.edu/kit/scc/sdm/grafana_backups.git'.format(git_user, git_token)
          repo = Repo.clone_from(repo_url,repo_path)


    folder_path = '{0}/{1}'.format(backup_dir, timestamp)
    log_file = 'info_backup_{0}.txt'.format(timestamp)
    file_path = folder_path + '/' + log_file

    if arg_components:
        arg_components_list = arg_components.split(',')

        # Backup only the components that provided via an argument
        for backup_function in arg_components_list:
            backup_functions[backup_function](args, settings)

        with open(u"{0}".format(file_path), 'w+') as f:
             f.write('Backup from {0}\n'.format(grafana_url) )
             f.write('Backup done only for component provided via argument: {0}\n'.format(arg_components) )
    else:
        # Backup every component
        for backup_function in backup_functions.keys():
            backup_functions[backup_function](args, settings)

        with open(u"{0}".format(file_path), 'w+') as f:
            f.write('Backup from {0}\n'.format(grafana_url) )
            f.write('Backup done for every component \n')

    aws_s3_bucket_name = settings.get('AWS_S3_BUCKET_NAME')
    azure_storage_container_name = settings.get('AZURE_STORAGE_CONTAINER_NAME')

#    if not arg_no_archive:
#        archive(args, settings)
 
  ###### Commit the backup folder to git repository #######
    repo = Repo(repo_path)
    remote = repo.remote()

    #set entire backup directory
    cwd = os.getcwd()
    backup_path = '{0}/{1}/{2}'.format(cwd,backup_dir,timestamp)

    #add backup directory and commit
    repo.index.add([backup_path])
    output= repo.index.commit( "Commit Grafana backup")

    try:        
        #push changes
        output = remote.push()
        print('Upload backup to git repository https://gitlab.kit.edu/kit/scc/sdm/grafana_backups.git: DONE')
        #remove backup folder from local disk
        shutil.rmtree(backup_path)
    except GitCommandError as e:
        print('Error: Could not push to origin master: {0}'.format(e))
        #remove backup folder since backup fails
        try:
           shutil.rmtree(backup_path)
        except OSError as e:
            print("Error: %s : %s" % (backup_path, e.strerror))


  
    if aws_s3_bucket_name:
        print('Upload archives to S3:')
        s3_upload(args, settings)

    if azure_storage_container_name:
        print('Upload archives to Azure Storage:')
        azure_storage_upload(args, settings)
