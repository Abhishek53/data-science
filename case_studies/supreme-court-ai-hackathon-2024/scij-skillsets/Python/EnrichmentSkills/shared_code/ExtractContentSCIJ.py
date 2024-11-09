# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import json
import logging
import os
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import os
import json
import logging
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

from urllib.parse import urlparse
import urllib.parse


#from dotenv import load_dotenv
# Load environment variables from .env file
#load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

storage_account_connection_string = os.environ["STORAGE_CONNECTION_STRING"]

content_folder_name = "sci-documents-text"  #content txt files storage container
content_container_name = "sci-data"  


def load_container_client(storage_account_connection_string, container_name):
    """
    This function establishes a connection with the Azure blob container and returns a container client.

    Parameters:
        account_name (str): The Azure storage account name.
        account_key (str): The Azure storage account key. 
        container_name (str): The name of the blob container in the storage account.
    
    Returns:
        tuple: a tuple containing a status code and the container client. On success, the status code is 1 and on failure, it is 0.
    """
    try:
        #sa_conn_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
        blob_service  = BlobServiceClient.from_connection_string(conn_str = storage_account_connection_string)
        container_client = blob_service.get_container_client(container_name)
        logging.info(f"Successfully loaded container client for container {container_name}")
        return 1, container_client
    except Exception as ex:
        logging.error(f"Failed to load container client for container {container_name}. Encountered exception: {ex}")
        return 0, None
    
def get_sci_content(document_url, content_container_client):

    container_name = content_container_client.container_name
    try:
        file_id_folder, extension = parse_document_url(document_url)

        # List blobs in the specified folder
        blob_list = content_container_client.list_blobs(name_starts_with=f"{content_folder_name}/{file_id_folder}")

        if blob_list:
            # Iterate through the blobs
            for blob in blob_list:
                # Check if the blob ends with ".json"
                logging.info(blob.name)
                if blob.name.endswith(".txt"):
                    # Read the content of the blob and convert it to a dictionary
                    blob_data = content_container_client.download_blob(blob)
                    blob_content = blob_data.readall().decode('utf-8')  # Assuming the file is encoded in UTF-8
                    return blob_content
        else:    
            return None
        # If no JSON file found, return an empty dictionary
    except Exception as e:
        logging.info(e)
        return None
    
def parse_document_url(document_url: str) -> tuple:
    """
    Parse the document URL and extract relevant information.

    Args:
        document_url (str): The URL of the document.

    Returns:
        tuple: A tuple containing container name, category class, report root folder, 
        relative folder path, and file name.
    """
    try:
        #parse url to url split result format
        # EX: SplitResult(scheme='https', netloc='bnlwestgscibd00036.blob.core.windows.net', path='/wor-sharepoint-to-blob-destination-container-dev/CATEGORY_DRINKS_CLASS_1/CW 10 0001/0149/CW100001_CW 14 0001-100070.docx', query='', fragment='')
        parsed_url = urlparse(document_url)
        file_path = parsed_url.path     #reference path
        relative_folder_path, file_name_with_extension = os.path.split(file_path) #seperate relative folder path and file name
        file_name, extension = os.path.splitext(file_name_with_extension) #seperate file name and extension
        file_id_folder = file_name 
        return file_id_folder, extension
    
    except Exception as ex:
        logging.error(f"Failed to fetch relative path for {document_url} ||| Encountered exception: {ex}")
        return "",""

def extract_content(document_url: str, content_container: BlobServiceClient):
    """
    Extract content from the document URL.

    Args:
        document_url (str): The URL of the document.
        content_container (BlobServiceClient): The content container
    Returns:
        dict: content extracted from the document URL.
    """
    container = content_container.container_name

    if container:
        
        sci_content = get_sci_content(document_url, content_container)
        return sci_content
           
    else:
        logging.info("Failed to load content container")
        return None


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    try:
        body = req.get_json()
        records = body["values"]

    except ValueError as e:
        logging.info(e)
        return func.HttpResponse("Body is not valid JSON.", status_code=400)
    
    try:
        container_connection_status, content_container_client = load_container_client(storage_account_connection_string, content_container_name)
        if not(container_connection_status):
            return func.HttpResponse("Failed To Load content Container.", status_code=400)
    except Exception as e:
        logging.info(e)
        return func.HttpResponse("Failed To Load content Container.", status_code=400)

    try:
        formatted_results = []
        for record in records:
            document_url = record["data"]["metadata_storage_path"]
            print(document_url)
            document_url = urllib.parse.unquote(document_url)
            content = extract_content(document_url, content_container_client)

            if content:
                result ={
                            "ExtractedContent" : content
                        }
            else:
                result = {
                            "ExtractedContent": ""
                        }
            logging.info(result)

            formatted_results.append( {
                                "recordId": record["recordId"],
                                "data":  result,
                                "error" : None,
                                "warnings": [{"message": ""} for w in []]
                            })

        return func.HttpResponse(
            result_to_json(formatted_results),
            mimetype="application/json",
        )
    except HttpResponseError as e:
        logging.info(e)
        return func.HttpResponse(
            "Received {0} response from contentSCIJ Skill:\n{1}".format(
                e.status_code, e.message
            ),
            status_code=400,
        )


def result_to_json(result):
    return json.dumps({"values": result}, default=vars)