from faster_whisper import WhisperModel
import assemblyai as aai

from abc import ABC, abstractmethod
from typing import Literal
import os
import asyncio
from concurrent.futures import ProcessPoolExecutor
from time import time


class AudioTranscriber(ABC):
    """
    A class for transcribing audio files.

    This class provides an abstract interface for transcribing audio files
    in different languages.

    Attributes:
        None

    Methods:
        transcribe: Transcribes an audio file.

    """

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def transcribe(self, audio_file: str, language_code: Literal["en", "fr"]) -> str:
        """
        Transcribes an audio file.

        Args:
            audio_file (str): The path to the audio file.
            language_code (Literal["en", "fr"]): The language code of the audio file.

        Returns:
            str: The transcribed text.
        """
        pass


class AsyncAudioTranscriber(ABC):
    """
    A class for transcribing audio files asynchronously.

    This class provides an abstract interface for transcribing audio files
    in different languages asynchronously.

    Attributes:
        None

    Methods:
        transcribe: Transcribes an audio file asynchronously.

    """

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    async def transcribe(
        self, audio_file: str, language_code: Literal["en", "fr"]
    ) -> str:
        """
        Transcribes an audio file asynchronously.

        Args:
            audio_file (str): The path to the audio file.
            language_code (Literal["en", "fr"]): The language code of the audio file.

        Returns:
            str: The transcribed text.
        """
        pass


class WhisperTranscriber(AudioTranscriber):
    """
    A class for transcribing audio files using the Whisper model.

    Attributes:
        model_name (str): The name of the Whisper model to use for transcription.
        cpu_threads (int): Number of threads to use when running on CPU (4 by default). A non zero value overrides the OMP_NUM_THREADS environment variable.
        num_workers (int): When transcribe() is called from multiple Python threads, having multiple workers enables true parallelism when running the model (concurrent calls to self.model.generate() will run in parallel). This can improve the global throughput at the cost of increased memory
    """

    def __init__(self):
        self.model_name = os.getenv("TRANSCRIBER_MODEL_NAME", "base")
        self.cpu_threads = 0
        self.num_workers = 1

        self.transcriber = WhisperModel(
            self.model_name,
            device="cpu",
            cpu_threads=self.cpu_threads,
            num_workers=self.num_workers,
            compute_type="int8",
        )

    def transcribe(self, audio_file: str, language_code: Literal["en", "fr"]) -> str:
        """
        Transcribes an audio file.

        Args:
            audio_file (str): The path to the audio file.
            language_code (Literal["en", "fr"]): The languag code of the audio file.

        Returns:
            str: The transcribed text.
        """
        start = time()
        segments, _ = self.transcriber.transcribe(
            audio_file, language=language_code, condition_on_previous_text=False
        )
        segments = [segment.text for segment in segments]
        text = " ".join(segments)
        end = time()

        print(f"Time to transcribe audio: {end - start:.2f}s")
        return text.strip()


class AssemblyAITranscriber(AudioTranscriber):
    """
    A class for transcribing audio files using the AssemblyAI API.

    Attributes:
        api_key (str): The AssemblyAI API key.
        client (assemblyai.Client): The AssemblyAI client.
    """

    def __init__(self):
        self.api_key = os.getenv("ASSEMBLYAI_API_KEY", None)
        assert (
            self.api_key is not None
        ), "ASSEMBLYAI_API_KEY environment variable is not set"

        aai.settings.api_key = self.api_key
        self.transcriber = aai.Transcriber()

    def transcribe(self, audio_file: str, language_code: Literal["en", "fr"]) -> str:
        """
        Transcribes an audio file.

        Args:
            audio_file (str): The path to the audio file.
            language_code (Literal["en", "fr"]): The language code of the audio file.

        Returns:
            str: The transcribed text.
        """
        config = aai.TranscriptionConfig(
            language_code=language_code, punctuate=True, format_text=True
        )

        start = time()
        transcript = self.transcriber.transcribe(audio_file, config=config)
        end = time()
        print(f"Time to transcribe audio: {end - start:.2f}s")

        if transcript.status == aai.TranscriptStatus.error:
            raise Exception(f"Transcription failed with error: {transcript.error}")

        return transcript.text.strip()


def transcribe_audio(
    transcriber, audio_file: str, language_code: Literal["en", "fr"]
) -> str:
    """
    Transcribes an audio file.

    Args:
        transcriber (WhisperModel): The Whisper model transcriber.
        audio_file (str): The path to the audio file.
        language_code (Literal["en", "fr"]): The languag code of the audio file.

    Returns:
        str: The transcribed text.
    """
    segments, _ = transcriber.transcribe(
        audio_file, language=language_code, condition_on_previous_text=False
    )
    segments = [segment.text for segment in segments]
    text = " ".join(segments)

    return text


class AynscWhisperTranscriber(AsyncAudioTranscriber):
    """
    An asynchronous class for transcribing audio files using the Whisper model.

    Attributes:
        model_name (str): The name of the Whisper model to use for transcription.
        cpu_threads (int): Number of threads to use when running on CPU (4 by default). A non zero value overrides the OMP_NUM_THREADS environment variable.
        num_workers (int): When transcribe() is called from multiple Python threads, having multiple workers enables true parallelism when running the model (concurrent calls to self.model.generate() will run in parallel). This can improve the global throughput at the cost of increased memory
    """

    def __init__(self):
        self.model_name = os.getenv("TRANSCRIBER_MODEL_NAME", "base")
        self.cpu_threads = 0
        self.num_workers = 1

        self.transcriber = WhisperModel(
            self.model_name,
            device="cpu",
            cpu_threads=self.cpu_threads,
            num_workers=self.num_workers,
            compute_type="int8",
        )

    async def transcribe(
        self, audio_file: str, language_code: Literal["en", "fr"]
    ) -> str:
        """
        Transcribes an audio file asynchronously.

        Args:
            audio_file (str): The path to the audio file.
            language_code (Literal["en", "fr"]): The language code of the audio file.

        Returns:
            str: The transcribed text.
        """
        start = time()
        loop = asyncio.get_running_loop()
        with ProcessPoolExecutor() as executor:
            text = await loop.run_in_executor(
                executor, transcribe_audio, self.transcriber, audio_file, language_code
            )
        end = time()
        print(f"Time to transcribe audio: {end - start:.2f}s")

        return text.strip()


class AsyncAssemblyAITranscriber(AsyncAudioTranscriber):
    """
    An asynchronous class for transcribing audio files using the AssemblyAI API.

    Attributes:
        api_key (str): The AssemblyAI API key.
        client (assemblyai.Client): The AssemblyAI client.
    """

    def __init__(self):
        self.api_key = os.getenv("ASSEMBLYAI_API_KEY", None)
        assert (
            self.api_key is not None
        ), "ASSEMBLYAI_API_KEY environment variable is not set"

        aai.settings.api_key = self.api_key
        self.transcriber = aai.Transcriber()

    async def transcribe(
        self, audio_file: str, language_code: Literal["en", "fr"]
    ) -> str:
        """
        Transcribes an audio file asynchronously.

        Args:
            audio_file (str): The path to the audio file.
            language_code (Literal["en", "fr"]): The language code of the audio file.

        Returns:
            str: The transcribed text.
        """
        config = aai.TranscriptionConfig(
            language_code=language_code, punctuate=True, format_text=True
        )

        start = time()
        future = self.transcriber.transcribe_async(audio_file, config=config)
        asyncio_future = asyncio.wrap_future(future)
        transcript = await asyncio_future
        end = time()
        print(f"Time to transcribe audio: {end - start:.2f}s")

        if transcript.status == aai.TranscriptStatus.error:
            raise Exception(f"Transcription failed with error: {transcript.error}")

        return transcript.text.strip()
