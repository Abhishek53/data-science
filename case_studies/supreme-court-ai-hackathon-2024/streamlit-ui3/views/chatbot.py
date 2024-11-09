import streamlit as st
#st.set_page_config(layout="wide")
from rag import answer_question
from hybrid_search import retrive_summary
from language_detection_tranlation import translate_text, language_detection

def format_response (response, summary=False):
    if summary:
         return f"**SUMMARY**\n{response['summary']}"  
    else:
         if response['answer'] == "None":
              return "Im sorry, Im Unable to answer that question"
         res = [response['answer']]
         res.extend(response['follow_up_questions'])
         return f"{res[0]}\n\nSuggested follow up questions:\n{res[1]}\n{res[2]}\n{res[3]}"
      

# Function to call the LLM (like GPT-3.5)
def call_llm(prompt, lang_code, case_number):
    if case_number != 'NA':
        response = retrive_summary(case_number)

    # Pass the language code to the LLM function
    else:        
        detected_lang = language_detection(prompt)
        print(prompt)
        print(detected_lang)
        if detected_lang != 'en':
            prompt = translate_text([prompt], ['en'])[0]
        print(prompt)
        response = answer_question(prompt)

    formatted_response = format_response(response, case_number != 'NA')
    if lang_code != 'en':
        formatted_response = translate_text([formatted_response], [lang_code])[0]

    return formatted_response

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Language selection dictionary
languages = {
    "English": "en",
    "Assamese": "as",
    "Bengali": "bn",
    "Bodo": "brx",
    "Dogri": "doi",
    "Gujarati": "gu",
    "Hindi": "hi",
    "Kannada": "kn",
    "Kashmiri": "ks",
    "Konkani": "kok",
    "Maithili": "mai",
    "Malayalam": "ml",
    "Manipuri": "mni",
    "Marathi": "mr",
    "Nepali": "ne",
    "Odia": "or",
    "Punjabi": "pa",
    "Sanskrit": "sa",
    "Santali": "sat",
    "Sindhi": "sd",
    "Tamil": "ta",
    "Telugu": "te",
    "Urdu": "ur"
}
case_numbers = ['NA','WRIT PETITION (CIVIL)/643/2015',
 'CIVIL APPEAL/7230/2024',
 'WRIT PETITION (CIVIL)/255/2024',
 'CIVIL APPEAL/4602/2024',
 'CIVIL APPEAL/5194/2024',
 'DIARYNO AND DIARYYR/8208/2024',
 'CRIMINAL APPEAL/3589/2023',
 'REVIEW PETITION (CIVIL)/1036/2023',
 'CIVIL APPEAL/6741/2024',
 'CRIMINAL APPEAL/437/2015',
 'SPECIAL LEAVE PETITION (CRIMINAL)/550/2024',
 'CRIMINAL APPEAL/1738/2024',
 'SPECIAL LEAVE PETITION (CIVIL)/10159/2020',
 'CIVIL APPEAL/4603/2024',
 'CIVIL APPEAL/4272/2024']
# Display language selection dropdown
# Create two columns for the dropdowns
# Configure the page layout to use the full width

col1, col2 = st.columns(2)
case_number = 'NA'
with col1:
    selected_language = st.selectbox("RESPONSE LANGUAGE", list(languages.keys()))

# Display case number selection dropdown in the second column
with col2:
    case_number = st.selectbox("CASE NUMBER", case_numbers)

lang_code = languages[selected_language]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call the LLM to generate a response
    response = call_llm(prompt, lang_code, case_number)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
