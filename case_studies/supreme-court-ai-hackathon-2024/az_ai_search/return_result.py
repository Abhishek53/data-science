from promptflow import tool
import json

@tool
def final_result() -> str:
    error_message = json.dumps({
        "answer": "I apologize, but I couldn't generate an answer. Try reformulating your question and be more specific or start a new conversation. It may also help to consider a different source or even narrow down the scope from within the Search page. Please also check <a href='https://unilever.sharepoint.com/sites/researchassistantv1/SitePages/Chat-and-Prompt-FAQs-for-the-R&D-Assistant.aspx?xsdata=MDV8MDJ8am9zaGJldHRzQG1pY3Jvc29mdC5jb218NjNmMjg3YjY4MWE4NGU0ODUzNDAwOGRjYTI2ZTFiNDB8NzJmOTg4YmY4NmYxNDFhZjkxYWIyZDdjZDAxMWRiNDd8MXwwfDYzODU2Mzg0MTAwOTgwNjE4M3xVbmtub3dufFRXRnBiR1pzYjNkOGV5SldJam9pTUM0d0xqQXdNREFpTENKUUlqb2lWMmx1TXpJaUxDSkJUaUk2SWsxaGFXd2lMQ0pYVkNJNk1uMD18MHx8fA==&sdata=NXFGOVU3bEdPb1htZStGTmVVclpjMndQRnY1WWhJcTdNdE5nMHhiSVl5Zz0='>Chat FAQ</a>",
        "follow_up_questions": [],
        "sources": []
    }, indent=2)

    model_output = wor_chat_35 if wor_chat_35 else wor_chat_4

    if gptchat35 or gptchat4:
        chat_data = gptchat35 if gptchat35 else gptchat4
        llm_chat = json.loads(chat_data)

        if llm_chat and llm_chat['answer'] == 'None':
            print("entered condition @ 25")
            return error_message
        else:
            # Ensure sources are not included
            llm_chat.pop("sources", None)
            return json.dumps(llm_chat, indent=2)
    else:
        try:
            if wor_chat_35:
                json_chat = json.loads(wor_chat_35)
                if '\\n' in json_chat.get('answer', '') or '\\n\\n' in json_chat.get('answer', ''):
                    json_chat['answer'] = json_chat['answer'].replace('\\n', '\n')

            else:
                json_chat = json.loads(wor_chat_4)
                if '\\n' in json_chat.get('answer', '') or '\\n\\n' in json_chat.get('answer', ''):
                    json_chat['answer'] = json_chat['answer'].replace('\\n', '\n')
        except Exception as e:
            model_output = wor_chat_35 if wor_chat_35 else wor_chat_4
            if "\"answer\":" not in model_output:
                json_chat = json.loads(json.dumps({"answer": model_output}))
                if '\\n' in json_chat.get('answer', '') or '\\n\\n' in json_chat.get('answer', ''):
                    json_chat['answer'] = json_chat['answer'].replace('\\n', '\n')
            else:
                print("entered condition @ 50")

                return error_message_json

    if json_chat and json_chat['answer'] == 'None':
        print("entered condition @ 55")

        return error_message
    else:
        if sources is not None and sources:
            source_list = []
            unique_sources = list(set(item.get('chunk_id', '') for item in sources))

            for source_id, source in enumerate(unique_sources):
                source_dict = {
                    "title": sources[source_id].get("title", ""),
                    "parent_id": sources[source_id].get("parent_id", ""),
                    "chunk_id": sources[source_id].get("chunk_id", ""),
                    "chunk_text": sources[source_id].get("chunk_text", "")
                }
                source_list.append(source_dict)

            json_chat["sources"] = source_list

        return json.dumps(json_chat, indent=2)
