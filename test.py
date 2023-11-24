import speech_recognition as sr

r = sr.Recognizer()
def speech_to_text():   
    with sr.Microphone() as source:
        print("Say something")
        audio_input = r.listen(source)
    
    try:
        text_input = r.recognize_whisper(audio_input, language="english")
        return text_input
    except sr.UnknownValueError:
        return "Whisper could not understand audio"
    except sr.RequestError as e:
        return "Could not request results from Whisper"
    
input = speech_to_text()
print(input)