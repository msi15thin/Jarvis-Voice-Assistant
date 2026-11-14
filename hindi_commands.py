HINDI_TO_ENGLISH = {
    "बैटरी": "battery",
    "समय": "time",
    "टाइम": "time",
    "सीपीयू": "cpu",
    "रैम": "ram",
    "स्क्रीनशॉट": "screenshot",
    "खोलो": "open",
    "खोलिए": "open",
    "ओपन": "open",
    "नोटपैड": "notepad",
    "कैलकुलेटर": "calculator",
    "क्रोम": "chrome",
    "गूगल": "google",
    "यूट्यूब": "youtube",
    "गिटहब": "github",
    "फ्लिपकार्ट": "flipkart",
    "अमेज़न": "amazon",
    "अमेजन": "amazon",
    "सर्च": "search",
    "खोजो": "search",
    "ढूंढो": "search",
    "चलाओ": "play",
    "बजाओ": "play",
    "प्ले": "play",
}


def normalize_hindi(command: str) -> str:
    out = command
    for hindi, english in HINDI_TO_ENGLISH.items():
        out = out.replace(hindi, english)
    return out