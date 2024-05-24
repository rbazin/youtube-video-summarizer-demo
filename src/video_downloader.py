from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound

import os
import aiofiles

from src.audio_transcriber import (
    AssemblyAITranscriber,
    AudioTranscriber,
    AsyncAudioTranscriber,
    AsyncAssemblyAITranscriber,
)


class VideoDownloader:
    """
    A class that handles downloading video transcripts and audio from YouTube.

    Attributes:
        transcript_dir (str): The directory to save downloaded transcripts.
        audio_dir (str): The directory to save downloaded audio files.
    """

    def __init__(self, transcript_dir="transcripts", audio_dir="audio"):
        self.transcriber: AudioTranscriber = AssemblyAITranscriber()
        self.transcript_dir = transcript_dir
        self.audio_dir = audio_dir
        os.makedirs(self.transcript_dir, exist_ok=True)
        os.makedirs(self.audio_dir, exist_ok=True)

    def get_transcript(self, video_url, language):
        """
        Downloads the transcript or audio for a given YouTube video.

        Args:
            video_url (str): The URL of the YouTube video.
            language (str): The language of the transcript to download.

        Returns:
            None
        """
        video_id = self.get_video_id(video_url)
        transcript = self._download_transcript(video_id, language)

        if transcript:
            print(f"Human transcript downloaded for video: {video_id}")
            transcript = "".join(obj["text"] for obj in transcript)
        else:
            audio_file = self._download_audio(video_url)
            print(f"Audio downloaded for video: {video_id}")
            print("Transcribing audio...")
            transcript = self._transcribe_audio(audio_file, language)
            print("Transcription complete.")

        self._save_transcript(transcript, video_id, language)
        print(f"Transcript saved for video: {video_id}")
        return transcript

    def get_video_id(self, video_url):
        """
        Extracts the video ID from a YouTube video URL.

        Args:
            video_url (str): The URL of the YouTube video.

        Returns:
            str: The video ID.
        """
        return YouTube(video_url).video_id

    def _download_transcript(self, video_id, language):
        """
        Downloads the transcript for a given YouTube video.

        Args:
            video_id (str): The ID of the YouTube video.
            language (str): The language of the transcript to download.

        Returns:
            str or None: The downloaded transcript, or None if not available.
        """
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        try:
            transcript = transcript_list.find_manually_created_transcript([language])
        except NoTranscriptFound:
            return None
        return transcript.fetch() if transcript else None

    def _save_transcript(self, transcript, video_id, language) -> str:
        """
        Saves the transcript to a file.

        Args:
            transcript (str): The transcript to save.
            video_id (str): The ID of the YouTube video.
            language (str): The language of the transcript.

        Returns:
            None
        """
        filename = f"{video_id}_{language}.txt"
        filepath = os.path.join(self.transcript_dir, filename)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(transcript)
        return str(filepath)

    def _download_audio(self, video_url) -> str:
        """
        Downloads the audio for a given YouTube video.

        Args:
            video_url (str): The URL of the YouTube video.
            video_id (str): The ID of the YouTube video.

        Returns:
            None
        """
        youtube = YouTube(video_url)
        audio_stream = youtube.streams.filter(only_audio=True).first()
        audio_path = audio_stream.download(output_path=self.audio_dir)
        return audio_path

    def _transcribe_audio(self, audio_file, language) -> str:
        """
        Transcribes the audio file.

        Args:
            audio_file (str): The path to the audio file.
            language (str): The language of the audio file.

        Returns:
            str: The transcribed text.
        """
        return self.transcriber.transcribe(audio_file, language)


class AsyncVideoDownloader:
    """
    An asynchronous class that handles downloading video transcripts and audio from YouTube.

    Attributes:
        transcript_dir (str): The directory to save downloaded transcripts.
        audio_dir (str): The directory to save downloaded audio files.
    """

    def __init__(self, transcript_dir="transcripts", audio_dir="audio"):
        self.transcriber: AsyncAudioTranscriber = AsyncAssemblyAITranscriber()
        self.transcript_dir = transcript_dir
        self.audio_dir = audio_dir
        os.makedirs(self.transcript_dir, exist_ok=True)
        os.makedirs(self.audio_dir, exist_ok=True)

    async def get_transcript(self, video_url, language):
        """
        Downloads the transcript or audio for a given YouTube video asynchronously.

        Args:
            video_url (str): The URL of the YouTube video.
            language (str): The language of the transcript to download.

        Returns:
            None
        """
        video_id = await self.get_video_id(video_url)
        transcript = await self._download_transcript(video_id, language)

        if transcript:
            print(f"Human transcript downloaded for video: {video_id}")
            transcript = "".join(obj["text"] for obj in transcript)
        else:
            audio_file = await self._download_audio(video_url)
            print(f"Audio downloaded for video: {video_id}")
            print("Transcribing audio...")
            transcript = await self._transcribe_audio(audio_file, language)
            print("Transcription complete.")
            os.remove(audio_file)
            print("Audio file deleted.")

        await self._save_transcript(transcript, video_id, language)
        print(f"Transcript saved for video: {video_id}")
        return transcript
    
    async def get_video_id(self, video_url):
        """
        Extracts the video ID from a YouTube video URL.

        Args:
            video_url (str): The URL of the YouTube video.

        Returns:
            str: The video ID.
        """
        return YouTube(video_url).video_id
    
    async def _download_transcript(self, video_id, language):
        """
        Downloads the transcript for a given YouTube video.

        Args:
            video_id (str): The ID of the YouTube video.
            language (str): The language of the transcript to download.

        Returns:
            str or None: The downloaded transcript, or None if not available.
        """
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        try:
            transcript = transcript_list.find_manually_created_transcript([language])
        except NoTranscriptFound:
            return None
        return transcript.fetch() if transcript else None

    async def _download_audio(self, video_url):
        """
        Downloads the audio for a given YouTube video asynchronously.

        Args:
            video_url (str): The URL of the YouTube video.

        Returns:
            str: The path to the downloaded audio file.
        """
        youtube = YouTube(video_url)
        audio_stream = youtube.streams.filter(only_audio=True).first()
        audio_path = audio_stream.download(output_path=self.audio_dir)
        return audio_path

    async def _save_transcript(self, transcript, video_id, language) -> str:
        """
        Saves the transcript to a file asynchronously.

        Args:
            transcript (str): The transcript to save.
            video_id (str): The ID of the YouTube video.
            language (str): The language of the transcript.

        Returns:
            str: The path to the saved transcript file.
        """
        filename = f"{video_id}_{language}.txt"
        filepath = os.path.join(self.transcript_dir, filename)

        async with aiofiles.open(filepath, "w", encoding="utf-8") as file:
            await file.write(transcript)

        return str(filepath)

    async def _transcribe_audio(self, audio_file, language):
        """
        Transcribes the audio file asynchronously.

        Args:
            audio_file (str): The path to the audio file.
            language (str): The language of the audio file.

        Returns:
            str: The transcribed text.
        """
        return await self.transcriber.transcribe(audio_file, language)
