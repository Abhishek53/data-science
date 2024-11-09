from hybrid_search import retrive_context_using_hybrid_search

from langchain_openai import AzureChatOpenAI
from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
import re
import os
from dotenv import load_dotenv
load_dotenv()


os.environ["OPENAI_API_VERSION"] = os.getenv("OPENAI_API_VERSION")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT")
os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
llm = AzureChatOpenAI(
    azure_deployment="akm-chat-35",  # or your deployment
    api_version="2023-06-01-preview",  # or your api version
    temperature=0
)

class LegalResponseParser(BaseOutputParser[dict]):
    """Custom parser for legal case responses using regex."""

    def parse(self, text: str) -> dict:
        # Define regex patterns for extracting the fields
        answer_pattern = re.compile(r"'answer':\s*\"([^\"]*)\"", re.DOTALL)
        follow_up_pattern = re.compile(r"'follow_up_questions':\s*\[(.*?)\]", re.DOTALL)
        
        # Extract the answer
        answer_match = answer_pattern.search(text)
        if not answer_match:
            raise OutputParserException("Could not find 'answer' in the response.")
        answer = answer_match.group(1).strip()

        # Extract the follow-up questions if present
        follow_up_questions = []
        follow_up_match = follow_up_pattern.search(text)
        if follow_up_match:
            follow_up_text = follow_up_match.group(1).strip()
            follow_up_questions = [q.strip().strip('"') for q in follow_up_text.split(',')]
        
        # Construct the final dictionary
        response_dict = {
            "answer": answer,
            "follow_up_questions": follow_up_questions
        }

        return response_dict

    @property
    def _type(self) -> str:
        return "legal_response_parser"

# Define the system and human message templates
system_message = SystemMessagePromptTemplate.from_template(
    """
Assistant helps the user with their questions related to legal research. You are knowledgeable in the legal domain and aim to answer the user's questions accurately, relying on case law, statutes, and legal principles. Only provide a response following the specified format without deviation. If you do not know the answer, return ['answer': "None"]. Do not provide incorrect answers. If asking a clarifying question to the user would help, ask the question.

If the user asks a question and you do not know the answer, return ['answer': "None"].

# Desired Output

Use this format to frame your answers:
Only provide a response following this format without deviation.

[
    'answer': "the answer to the user's question, specific to the legal domain",
    'follow_up_questions': [ 
        "a comma separated list of three follow up questions that can be asked to build on your answer, related to legal research"
    ]
]
You must only use this format; you are not allowed to change the format.

# List of Examples

EXAMPLE
Conversation history:
USER: What is the doctrine of stare decisis?
ASSISTANT: [
    'answer': "The doctrine of stare decisis is a legal principle that courts should follow precedents established in previous cases when making rulings in similar cases. It ensures consistency and stability in the law.",
    'follow_up_questions': [
        "What are some landmark cases that established important precedents under the doctrine of stare decisis?",
        "How does the doctrine of stare decisis influence judicial decision-making in different jurisdictions?",
        "Can the doctrine of stare decisis ever be overturned or disregarded by a court?"
    ]
]
END OF EXAMPLE

EXAMPLE
Conversation history:
USER: What are the key differences between civil and criminal law?
ASSISTANT: [
    'answer': "Civil law deals with disputes between individuals or organizations, typically involving private rights, whereas criminal law involves offenses against the state or public, where the government prosecutes the offender. The burden of proof is higher in criminal cases, requiring proof beyond a reasonable doubt, while civil cases require a preponderance of evidence.",
    'follow_up_questions': [ 
        "What are some examples of cases that would fall under civil law?",
        "How does the burden of proof differ between civil and criminal cases?",
        "What are the potential penalties or remedies in civil law compared to criminal law?"
    ]
]
END OF EXAMPLE

EXAMPLE
Conversation history:
USER: Can a contract be enforced if it was made under duress?
ASSISTANT: [
    'answer': "A contract made under duress is generally considered voidable, meaning the party who was forced into the agreement can choose to either enforce or void the contract. Duress involves coercion or threats that deprive a party of free will in entering into the contract.",
    'follow_up_questions': [
        "What legal remedies are available for a party seeking to void a contract made under duress?",
        "How do courts determine whether duress was present when a contract was formed?",
        "Are there any exceptions where a contract made under duress might still be enforceable?"
    ]
]
END OF EXAMPLE

EXAMPLE
Conversation history:
USER: What's the current population of the United States?
ASSISTANT: ['answer': "None"]
END OF EXAMPLE

# Return ['answer': "None"] if the question cannot be answered.
# Return in the desired list format if you can answer.
"""
)

def generate_human_prompt(context_data):

    content = [
        f"""<CHUNK {i+1} START>
    ## Chunk Text: {item['chunk_text']}
    ## Chunk Score: {item['score']}
    <CASE METADATA START>
    ## Case Title: {item['case_title']}
    ## Judges: {item['judges']}
    ## Issue For Consideration Backgroud:  {item['issue_for_consideration']}
    <CASE METADATA END>
    <CHUNK {i+1} END>
    """
        for i,item in enumerate(context_data)
    ]

    human_prompt = f"""You can only answer questions where the answers can be found in this context given below: \n<CONTEXT START>\n"""
    human_prompt += "\n".join(content)
    human_prompt += "\n<CONTEXT END>"
    return human_prompt


def generate_human_prompt_rag(question):
    context_data = retrive_context_using_hybrid_search(question)
    human_prompt = generate_human_prompt(context_data)
    return human_prompt



def answer_question(input_question):

    human_prompt = generate_human_prompt_rag(input_question)
    human_message = HumanMessagePromptTemplate.from_template(human_prompt+"{question}")

    # Create the ChatPromptTemplate from the messages
    prompt = ChatPromptTemplate.from_messages([system_message, human_message])
    output_parser = LegalResponseParser()
    chain = prompt|llm|output_parser
    # Now you can use this prompt template in your chain or model invocation
    llm_response = chain.invoke({"question": input_question})
    return llm_response
