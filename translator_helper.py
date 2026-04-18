"""
Translator Helper
Using deep-translator
Compatible with Python 3.14
"""

from deep_translator import GoogleTranslator

# cache for speed

translation_cache = {}

def clean_text(text):

    text = text.replace("_", " ")

    text = text.strip()

    return text


def translate_to_arabic(text):

    text = clean_text(text)

    # check cache first

    if text in translation_cache:

        return translation_cache[text]

    try:

        arabic = GoogleTranslator(
            source="auto",
            target="ar"
        ).translate(text)

        translation_cache[text] = arabic

        return arabic

    except:

        return text