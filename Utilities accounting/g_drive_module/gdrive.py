from __future__ import print_function

from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload,MediaFileUpload
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import io
import pprint


pp = pprint.PrettyPrinter(indent=4)

# authorization with service_account
SCOPES = ['https://www.googleapis.com/auth/drive']
# SERVICE_ACCOUNT_FILE = Path(Path.cwd().parent, "g_drive_module", "counter-metters-9752b22e3166.json")
# SERVICE_ACCOUNT_FILE = "counter-metters-9752b22e3166.json"
SERVICE_ACCOUNT_FILE = r"g_drive_module\counter-metters-9752b22e3166.json"

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)




# create files v2 little faster
def create_file_v2(list_fle):
    for name in list_fle:
        file_metadata = {'name': name, 'parents': ['17SNsgn998gpAdksKnMnCxS3HPXvD9w8P']}
        media = MediaFileUpload(f"Counters_Database/{name}", resumable=True)
        service.files().create(body=file_metadata, media_body=media).execute()


# create folder in parent folder
def create_folder(name_folder):
    folder_id = '17SNsgn998gpAdksKnMnCxS3HPXvD9w8P'
    name = name_folder
    file_metadata = {
                    'name': name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': 'Folder-Test'
                    # 'parents': [folder_id]
                }
    r = service.files().create(body=file_metadata, fields='id').execute()
    return r


# delete file
def delete_fiile(fileid):
    file_id = fileid
    service.files().delete(fileId=file_id).execute()


# print list of files in service account
def list_files_gdrive():
    results = service.files().list(
        pageSize=100,
        fields="nextPageToken, files(name, id)",
    q="'17SNsgn998gpAdksKnMnCxS3HPXvD9w8P' in parents"
    ).execute()
    files_res = results["files"]
    return files_res


# delete files use batch request (faster)
def callback(request_id, response, exception):
    if exception:
        print("Exception:", exception)

def del_batch(list_file_id):

    batch = service.new_batch_http_request(callback=callback)

    for file_id in list_file_id:
        batch.add(service.files().delete(fileId=file_id))

    batch.execute()


# download files from gdrive
def download_file(list_download):
    # file_id = '1HKC4U1BMJTsonlYJhUKzM-ygrIVGzdBr'
    # request = service.files().get_media(fileId=file_id)
    # filename = '/home/makarov/File.csv'
    # fh = io.FileIO(filename, 'wb')
    # # fh = io.FileIO()
    # downloader = MediaIoBaseDownload(fh, request)
    # done = False
    # while done is False:
    #     status, done = downloader.next_chunk()
    #     print("Download %d%%." % int(status.progress() * 100))


    for item in list_download:
        request = service.files().get_media(fileId=item['id'])
        filename = f"Counters_Database2/{item['name']}"
        fh = io.FileIO(filename, 'wb')
        # fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while done is False:
            status, done = downloader.next_chunk()
    print("Download %d%%." % int(status.progress() * 100))