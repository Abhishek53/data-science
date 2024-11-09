from promptflow import tool
import os, json
import openai
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType, QueryLanguage
# from azure.search.documents.models import VectorizableTextQuery

@tool
def cog_search(search_text, vectors, document_ids, restricted, permissions, chunks, source):
    vectors=vectors
    service_endpoint: str = "https://resassistantunlvrsrchdev.search.windows.net"
    key: str = ""
    index_name: str = "main"
    

    if source == "scij":
        index_name= "tascp"
    elif source == "elsn":
        index_name = "elsn"
    
    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    # process permissions list
    permissions_string = ','.join(permissions)
    print(permissions_string)

    # Set default value 
    filter_condition = None

    # Check for BYOD
    if restricted is True and permissions:
        filter_condition = f"restricted eq true and permissions/any(t: t eq '{permissions_string}')"

    # Check for only WOR
    if restricted is False and not permissions:
        filter_condition = f"restricted eq false"

    # Check for both WOR & BYOD
    if restricted is False and permissions:
        filter_condition = f"restricted eq false or permissions/any(t: t eq '{permissions_string}')"

    # Add document_ids to the filter_condition if they exist
    if document_ids:
        document_string = ','.join(document_ids)
        document_filter = f"search.in(parent_id, '{document_string}') or search.in(index_key, '{document_string}')"
        
        # Append the document_filter to the existing filter_condition
        if filter_condition:
            filter_condition = f"(({filter_condition}) and ({document_filter}))"
        else:
            filter_condition = document_filter

    results_list = search_client.search(  
                search_text,  
                filter=filter_condition,   
                query_type=QueryType.SEMANTIC,
                query_language=QueryLanguage.EN_US, 
                #select=["index_key", "chunk", "title", "parent_id", "permissions", "restricted"],   
                semantic_configuration_name="default",  
                top=chunks,  
                query_caption="extractive|highlight-false",  
                vector=vectors,  
                top_k=50 if vectors else None,  
                vector_fields="vector" ,
                #if vectors else None,  
            )
    # Initialize a list to store the results as dictionaries
    result_dict_list = []
    
    for item in results_list:
        print(item)
        result_dict = {
            'title': item['title'],
            'parent_id': item['parent_id'],
            'chunk_id': item['index_key'],
            'chunk_text': item['chunk'],
            # 'content': item['content'],
            'score': item['@search.score'],
            'reranker_score': item['@search.reranker_score'],
            'restricted': item['restricted'],
            #'permissions': item['permissions']
        }

        # Add search captions information
        captions = item.get('@search.captions', [])
        if captions:
            caption = captions[0]
            result_dict['caption_text'] = caption.text if hasattr(caption, 'text') else ''
            result_dict['caption_highlights'] = caption.highlights if hasattr(caption, 'highlights') else ''

        result_dict_list.append(result_dict)

    return result_dict_list