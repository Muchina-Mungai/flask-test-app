from azure.identity import ClientSecretCredential,ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient
import mysql.connector 
from dotenv import load_dotenv
import os

load_dotenv()
client_id=os.environ['AZURE_CLIENT_ID']
tenant_id=os.environ['AZURE_TENANT_ID']
client_secret=os.environ['AZURE_CLIENT_SECRET']
vault_uri=os.environ['AZURE_VAULT_URL']
storage_account_url=os.environ['AZURE_STORAGE_URL']
credentials=ClientSecretCredential(tenant_id,client_id,client_secret)



def get_secret(secretName):
    secret_name=secretName
    secret_client=SecretClient(vault_url=vault_uri,credential=credentials)
    secret_value=secret_client.get_secret(secret_name)
    return secret_value.value

def get_blob_storage(container_name,blob_name,account_url=storage_account_url):
    blob_service_client=BlobServiceClient(account_url,credential=credentials)
    container_service_client=blob_service_client.get_container_client(container=container_name)
    blob_client=container_service_client.get_blob_client(blob=blob_name)
    data = blob_client.download_blob().readall()
    return data

def upload_blob(file_path,container_name,file_name,account_url=storage_account_url):
    blob_service_client=BlobServiceClient(account_url,credential=credentials)
    container_service_client=blob_service_client.get_container_client(container=container_name)
    with open(file_path,"r") as fh:
        data=fh.read()
        container_service_client.upload_blob(name=file_name,data=data)
        
def get_blob_container_client(container_name,account_url=storage_account_url):
    blob_service_client=BlobServiceClient(account_url,credential=credentials)
    container_service_client=blob_service_client.get_container_client(container=container_name)
    return container_service_client
    
def access_database():
    try:
        managed_identity_client_id=os.getenv('AZURE_MYSQL_CLIENT_ID')    
        credential=ManagedIdentityCredential(client_id=managed_identity_client_id)
        access_token=credential.get_token('https://ossrdbms-aad.database.windows.net/.default')
        host=os.getenv('AZURE_MYSQL_HOST')
        database=os.getenv('AZURE_MYSQL_NAME')
        user=os.getenv('AZURE_MYSQL_USER')
        password=access_token.token
        cnx=mysql.connector.connect(user=user,
                                    password=password,
                                    host=host,
                                    database=database
        )
        data_cursor=cnx.cursor()
        data_cursor.execute("SHOW TABLES")
        for x in data_cursor:
            print(x)
        return "Returned from database"
    except Exception as e:
        print(e)
    finally:
        cnx.close()
        return "Ambiguous"
    
   
    
    
