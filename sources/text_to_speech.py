from kokoro import KPipeline
from IPython.display import display, Audio
import soundfile as sf
import subprocess
import re
import platform

class Speech():
    """
    Speech is a class for generating speech from text.
    """
    def __init__(self, language: str = "english", voice_idx: int = 0) -> None:
        self.lang_map = {
            "english": 'a',
            "chinese": 'z',
            "french": 'f',
            "spanish": 'e'
        }
        self.voice_map = {
            "english": ['af_bella', 'af_sky', 'af_alloy', 'af_kore', 'af_nicole', 'af_nova', 'am_echo', 'am_michael', 'am_puck'],
            "chinese": ['zf_xiaobei', 'zf_xiaoni', 'zf_xiaoxiao', 'zf_xiaoyi', 'zm_yunjian', 'zm_yunxi', 'zm_yunxia', 'zm_yunyang'],
            "french": ['ff_siwis'],
            "spanish": ['ef_dora', 'em_alex', 'em_santa']
        }

        if language not in self.lang_map:
            print(f"Language {language} not supported. Defaulting to English.")
            language = "english"
        if voice_idx >= len(self.voice_map[language]):
            print(f"Voice index {voice_idx} not found. Defaulting to 0.")
            voice_idx = 0

        self.pipeline = KPipeline(lang_code=self.lang_map[language])
        self.voice = self.voice_map[language][voice_idx]
        self.speed = 1.2
        self.language = language
        self.voice_number = voice_idx
        print(f"Language: {language} voice: {self.voice}")

    def speak(self, sentence: str, language: str|None = None, voice_idx: int|None = None):
        """
        Convert text to speech using an AI model and play the audio.

        Args:
            sentence (str): The text to convert to speech. Will be pre-processed.
            language (str, optional): The language to use for speech synthesis.
            voice_idx (int, optional): Index of the voice to use from the voice map.
        """
        if language is None:
            language = self.language
        if voice_idx is None:
            voice_idx = self.voice_number
        sentence = self.clean_sentence(sentence)
        self.voice = self.voice_map[language][voice_idx]
        generator = self.pipeline(
            sentence, voice=self.voice,
            speed=self.speed, split_pattern=r'\n+'
        )
        for i, (gs, ps, audio) in enumerate(generator):
            audio_file = 'sample.wav'
            display(Audio(data=audio, rate=24000, autoplay=i==0), display_id=False)
            sf.write(audio_file, audio, 24000) # save each audio file
            if platform.system().lower() == "windows":
                import winsound
                winsound.PlaySound(audio_file, winsound.SND_FILENAME)
            elif platform.system().lower() == "linux":
                #for WSL we might want to use ffplay.exe (from windows) to play the audio to get better quality and latency
                if "microsoft-standard-WSL2" in platform.uname().release:
                    subprocess.call(["ffplay.exe", "-nodisp", "-autoexit", "-loglevel", "panic", audio_file])
                else:
                    subprocess.call(["aplay", audio_file])
            else:
                subprocess.call(["afplay", audio_file])

    def replace_url(self, url: re.Match) -> str:
        """
        Replace URL with domain name or empty string if IP address.
        Args:
            url (re.Match): Match object containing the URL pattern match
        Returns:
            str: The domain name from the URL, or empty string if IP address
        """
        domain = url.group(1)
        if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain):
            return ''
        return domain

    def extract_filename(self, m: re.Match) -> str:
        """
        Extract filename from path.
        Args:
            m (re.Match): Match object containing the path pattern match
        Returns:
            str: The filename from the path
        """
        path = m.group()
        parts = re.split(r'/|\\', path)
        return parts[-1] if parts else path
    
    def shorten_paragraph(self, sentence):
        """
        Shorten paragraph like **explaination**: <long text> by keeping only the first sentence.
        Args:
            sentence (str): The sentence to shorten
        Returns:
            str: The shortened sentence
        """
        lines = sentence.split('\n')
        lines_edited = []
        for line in lines:
            if line.startswith('**'):
                lines_edited.append(line.split('.')[0])
            else:
                lines_edited.append(line)
        return '\n'.join(lines_edited)

    def clean_sentence(self, sentence):
        """
        Clean and normalize text for speech synthesis by removing technical elements.
        Args:
            sentence (str): The input text to clean
        Returns:
            str: The cleaned text with URLs replaced by domain names, code blocks removed, etc..
        """
        lines = sentence.split('\n')
        filtered_lines = [line for line in lines if re.match(r'^\s*[¡¿a-zA-ZáéíóúñüÁÉÍÓÚÑÜ]', line)]
        sentence = '. '.join(filtered_lines)
        sentence = re.sub(r'`.*?`', '', sentence)
        sentence = re.sub(r'https?://(?:www\.)?([^\s/]+)(?:/[^\s.]*)?', self.replace_url, sentence)
        sentence = re.sub(r'\b[\w./\\-]+\b', self.extract_filename, sentence)
        sentence = re.sub(r'\b-\w+\b', '', sentence)
        sentence = re.sub(r'[^a-zA-Z0-9:;.,!?_ -áéíóúñüÁÉÍÓÚÑÜ]+', ' ', sentence)
        sentence = re.sub(r'\s+', ' ', sentence).strip()
        if self.language == "spanish":
            sentence = sentence.replace('.com', ' punto com')
        else:
            sentence = sentence.replace('.com', ' dot com')
        print(sentence)
        return sentence

if __name__ == "__main__":
    just_one_voice = True
    speech = Speech()
    tosay = """
    I looked up recent news using the website https://www.theguardian.com/world
    Here is how to list files:
    ls -l -a -h
    the ip address of the server is 192.168.1.1
    """
    for voice_idx in range (len(speech.voice_map["english"])):
        print(f"Voice {voice_idx}")
        speech.speak(tosay, voice_idx=voice_idx)
        if just_one_voice:
            break


    speech_es = Speech(language="spanish")
    tosay = """
    ¡Hola!
    He ojeado las noticias en el sitio web https://www.theguardian.com/world
    Así es como se enumeran los archivos:
    ls -l -a -h
    la dirección IP del servidor es 192.168.1.1
    """
    for voice_idx in range (len(speech_es.voice_map["spanish"])):
        print(f"Voice {voice_idx}")
        speech_es.speak(tosay, voice_idx=voice_idx)
        if just_one_voice:
            break