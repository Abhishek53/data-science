import streamlit as st
#st.set_page_config(layout="wide")
from rag import answer_question
from language_detection_tranlation import translate_text, language_detection

def format_response(response, summary=False):
    if summary:
        return f"**SUMMARY**\n{response['summary']}"  
    else:
        if response['answer'] == "None":
            return "I'm sorry, I'm unable to answer that question"
        res = [response['answer']]
        res.extend(response['follow_up_questions'])
        return res

# Function to call the LLM (like GPT-3.5)
def call_llm(prompt, lang_code):
    detected_lang = language_detection(prompt)
    print(prompt)
    print(detected_lang)
    if detected_lang != 'en':
        prompt = translate_text([prompt], ['en'])[0]
    print(prompt)
    response = answer_question(prompt)

    formatted_response = format_response(response)
    if lang_code != 'en':
        formatted_response[0] = translate_text([formatted_response[0]], [lang_code])[0]

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

selected_language = st.selectbox("RESPONSE LANGUAGE", list(languages.keys()))

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
    response = call_llm(prompt, lang_code)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response[0])
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response[0]})

        st.markdown("**Suggested follow up questions:**")
        for i, question in enumerate(response[1:], start=1):
            if st.button(question, key=f"followup_{i}"):
                st.session_state.messages.append({"role": "user", "content": question})
                response = call_llm(question, lang_code)
                st.session_state.messages.append({"role": "assistant", "content": response[0]})
                st.experimental_rerun()
