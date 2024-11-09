from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

# Initialize the client
cog_service_endpoint = "https://vsent-sub-cog-services.cognitiveservices.azure.com/"
cog_service_key = ""
credential = AzureKeyCredential(cog_service_key)
text_translator = TextTranslationClient(endpoint=cog_service_endpoint, credential=credential)
language_detection_client = TextAnalyticsClient(endpoint=cog_service_endpoint, credential=credential)

# Example method for detecting the language of text
def language_detection(documents):
    try:
        response = language_detection_client.detect_language(documents = documents, country_hint = 'us')[0]
        print("Language: ", response.primary_language.name)
        return response.primary_language.iso6391_name

    except Exception as err:
        print("Encountered exception. {}".format(err))

def translate_text(input_text_elements, to_language):
    try:

        response = text_translator.translate(body=input_text_elements, to_language=to_language)
        translations = response[0:] if response else None

        output_text_elements = []

        for translation in translations:
            if translation:
                detected_language = translation.detected_language
                if detected_language:
                    print(
                        f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}."
                    )
                for translated_text in translation.translations:
                    output_text_elements.append(translated_text.text)
                    print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")

        return output_text_elements

    except Exception as exception:
        print(exception)

