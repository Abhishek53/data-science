
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType, QueryLanguage
# from azure.search.documents.models import VectorizableTextQuery
from dotenv import load_dotenv
load_dotenv("../.env")
import os
from openai import AzureOpenAI

az_oai_client = AzureOpenAI(
  api_key = os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version = os.getenv("OPENAI_API_VERSION"),
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
)

def generate_embeddings(text, model="akm-embeddings"): # model = "deployment_name"
    return az_oai_client.embeddings.create(input = [text], model=model).data[0].embedding

def cog_search(search_text, vectors, document_ids, restricted, permissions, chunks, source):
    vectors=vectors
    service_endpoint: str = "https://vs-end-sub-aisearch.search.windows.net"
    key: str = ""
    index_name: str = "scij-index"
    
    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    results_list = search_client.search(  
                search_text,    
                query_type=QueryType.SIMPLE,
                query_language=QueryLanguage.EN_US, 
                #select=["index_key", "chunk", "title", "parent_id", "permissions", "restricted"],   
                semantic_configuration_name="default",  
                top=chunks,  
                #query_caption="extractive|highlight-false",  
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
            'case_title': item['case_title'],
            'case_number': item['case_number'],
            'disposal_nature': item['disposal_nature'],
            'direction_issue': item['direction_issue'],
            'judges': item['judges'],
            'issue_for_consideration': item['issue_for_consideration'],
            'head_notes': item['head_notes'],
            'decision_date': item['decision_date'],
            'metadata_storage_path': item['metadata_storage_path'],
            'chunk_text': item['chunk'],
            # 'content': item['content'],
            'score': item['@search.score'],
            'reranker_score': item['@search.reranker_score'],
            #'permissions': item['permissions']
        }

        # Add search captions information
        """
        captions = item.get('@search.captions', [])
        if captions:
            caption = captions[0]
            result_dict['caption_text'] = caption.text if hasattr(caption, 'text') else ''
            result_dict['caption_highlights'] = caption.highlights if hasattr(caption, 'highlights') else ''
        """
        result_dict_list.append(result_dict)


    return result_dict_list

def retrive_context_using_hybrid_search(question):
  vector_embeddings =  generate_embeddings(question)
  context_data = cog_search(question, vector_embeddings, [], False, [], 3, "scij-index")
  return context_data

def retrive_summary(case_number):
    service_endpoint: str = "https://vs-end-sub-aisearch.search.windows.net"
    key: str = ""
    index_name: str = "scij-index"
    
    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    results_list = search_client.search(  
                "*",    
                query_type=QueryType.SIMPLE,
                query_language=QueryLanguage.EN_US, 
                #select=["judgement_sumary"],
                filter=f"parent_id eq null and case_number eq ' {case_number}'",   
                semantic_configuration_name="default",  
                
            )
    # Initialize a list to store the results as dictionaries
    
    for item in results_list:
        return {"summary" : item['judgement_summary']}