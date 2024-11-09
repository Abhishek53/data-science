
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
        print(text)
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
Assistant helps the user with their questions related to any domain. You are knowledgeable in any domain and aim to answer the user's questions accurately, Only provide a response following the specified format without deviation.

# Desired Output

Use this format to frame your answers:
Only provide a response following this format without deviation.

[
    'answer': "the answer to the user's question, specific to the domain",
    'follow_up_questions': [ 
        "a comma separated list of three follow up questions that can be asked to build on your answer, related to the domain"
    ]
]
You must only use this format; you are not allowed to change the format.

# List of Examples

EXAMPLE
Conversation history:
USER: What is the theory of relativity?
ASSISTANT: [
    'answer': "The theory of relativity, developed by Albert Einstein, encompasses two interrelated theories: special relativity and general relativity. Special relativity deals with the relationship between space and time, while general relativity explains the gravitational force as a curvature of spacetime caused by mass.",
    'follow_up_questions': [
        "How did Einstein's theory of relativity change our understanding of physics?",
        "What are some practical applications of the theory of relativity?",
        "Can you explain the difference between special relativity and general relativity?"
    ]
]
END OF EXAMPLE

EXAMPLE
Conversation history:
USER: What are the key differences between machine learning and deep learning?
ASSISTANT: [
    'answer': "Machine learning is a subset of artificial intelligence that involves training algorithms to learn patterns from data and make predictions. Deep learning is a further subset of machine learning that uses neural networks with many layers (hence 'deep') to model complex patterns in large datasets.",
    'follow_up_questions': [ 
        "What are some common applications of machine learning?",
        "How do neural networks in deep learning work?",
        "What are the advantages and disadvantages of deep learning compared to traditional machine learning?"
    ]
]
END OF EXAMPLE

EXAMPLE
Conversation history:
USER: Can you explain the concept of supply and demand in economics?
ASSISTANT: [
    'answer': "Supply and demand is a fundamental economic model that describes how prices are determined in a market. The law of demand states that, all else being equal, as the price of a good or service decreases, the quantity demanded increases. Conversely, the law of supply states that as the price increases, the quantity supplied increases. The equilibrium price is where the quantity demanded equals the quantity supplied.",
    'follow_up_questions': [
        "What factors can cause shifts in supply and demand curves?",
        "How does the concept of elasticity relate to supply and demand?",
        "Can you provide examples of how supply and demand affect prices in real-world markets?"
    ]
]
END OF EXAMPLE

EXAMPLE
Conversation history:
USER: What's the future of AI?
ASSISTANT: ['answer': "None"]
END OF EXAMPLE

# Return ['answer': "None"] if the question cannot be answered.
# Return in the desired list format if you can answer.
"""
)

def generate_human_prompt(context_data=""):

    content = context_data
    human_prompt = f"""Please answer as detailed as possible\n"""
    human_prompt += "\n".join(content)
    return human_prompt


def generate_human_prompt_rag(question):
    #context_data = retrive_context_using_hybrid_search(question)
    human_prompt = generate_human_prompt()
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
    print(llm_response)
    return llm_response
