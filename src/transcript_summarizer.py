from groq import Groq, AsyncGroq, BadRequestError
from pydantic import BaseModel, ValidationError
from json_repair import repair_json

import re
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List

from src.prompts.summarizer_prompts import (
    CHUNK_SUMMARIZER_PROMPT,
    SUMMARIES_MERGER_PROMPT,
)


class ResponseModel(BaseModel):
    scratchpad: str
    summary: str


class TranscriptSummarizer:
    """
    A class for summarizing long YouTube video transcriptions using calls to large language model APIs.
    """

    def __init__(self, max_chunk_size=1000):
        """
        Initialize the TranscriptSummarizer.

        Args:
            api_key (str): The API key required for authentication with the language model API.
            api_url (str): The URL of the language model API endpoint for summarization.
            max_chunk_size (int, optional): The maximum size of each chunk in characters. Default is 1000.
        """
        self.api_key = os.getenv("GROQ_API_KEY", None)
        assert self.api_key, "GROQ_API_KEY environment variable is not set"
        self.client = Groq(
            api_key=self.api_key,
        )
        self.model_name = os.getenv("SUMMARIZER_MODEL_NAME", "llama3-8b-8192")
        self.max_chunk_size = max_chunk_size
        self.max_tokens = 8000

    def split_in_chunks(self, transcript: str) -> List[str]:
        """
        Split the transcript into smaller chunks based on the max_chunk_size.

        Args:
            transcript (str): The full transcript text to be summarized.

        Returns:
            list: A list of strings, where each string represents a chunk of the transcript.
        """
        paragraphs = re.split(r"\n{2,}", transcript)
        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 1 <= self.max_chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return [chunk for chunk in chunks if chunk]

    def summarize_chunk(self, chunk: str, language) -> str:
        """
        Summarize a chunk of the transcript using the language model API.

        Args:
            chunk (str): A chunk of the transcript text to be summarized.

        Returns:
            str: The summary of the given chunk.

        Raises:
            requests.exceptions.RequestException: If there is an error with the API request.
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": CHUNK_SUMMARIZER_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": "<chunk>\n\n" + chunk + "\n\n</chunk>",
                    },
                ],
                model=self.model_name,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"},
            )
            print(chat_completion.choices[0].message.content)
            response = ResponseModel.model_validate_json(
                chat_completion.choices[0].message.content
            )
        except BadRequestError as e:
            repaired_json_dict = repair_json(
                e.body["error"]["failed_generation"], return_objects=True
            )
            response = ResponseModel.model_validate(repaired_json_dict)
        except ValidationError:
            repaired_json_dict = repair_json(
                chat_completion.choices[0].message.content, return_objects=True
            )
            response = ResponseModel.model_validate(repaired_json_dict)

        return response.summary

    def merge_summaries(self, summaries: List[str]) -> str:
        """
        Merge the summaries of all chunks into a final summary.

        Args:
            summaries (list): A list of strings, where each string represents a summary of a chunk.

        Returns:
            str: The final summary of the entire transcript.
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": SUMMARIES_MERGER_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": "<summaries>\n\n"
                        + "\n\n".join(summaries)
                        + "\n\n</summaries>",
                    },
                ],
                model=self.model_name,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"},
            )

            print(chat_completion.choices[0].message.content)
            response = ResponseModel.model_validate_json(
                chat_completion.choices[0].message.content
            )
        except BadRequestError as e:
            repaired_json_dict = repair_json(
                e.body["error"]["failed_generation"], return_objects=True
            )
            response = ResponseModel.model_validate(repaired_json_dict)
        except ValidationError:
            repaired_json_dict = repair_json(
                chat_completion.choices[0].message.content, return_objects=True
            )
            response = ResponseModel.model_validate(repaired_json_dict)

        return response.summary

    def summarize(self, transcript: str, language) -> str:
        """
        Summarize the entire transcript by splitting it into chunks, summarizing each chunk, and combining the summaries.

        Args:
            transcript (str): The full transcript text to be summarized.

        Returns:
            str: The final summary of the entire transcript.
        """
        print("Summarizing the transcript")

        chunks = self.split_in_chunks(transcript)

        print(f"Summarizing {len(chunks)} chunks separately")
        with ThreadPoolExecutor() as executor:
            summaries = list(
                executor.map(
                    lambda chunk: self.summarize_chunk(chunk, language), chunks
                )
            )

        print("Merging the summaries chunks into ")
        final_summary = self.merge_summaries(summaries)

        return final_summary


class AsyncTranscriptSummarizer:
    """
    A class for summarizing long YouTube video transcriptions asynchronously using calls to large language model APIs.
    """

    def __init__(self, max_chunk_size=1000):
        """
        Initialize the TranscriptSummarizer.

        Args:
            api_key (str): The API key required for authentication with the language model API.
            api_url (str): The URL of the language model API endpoint for summarization.
            max_chunk_size (int, optional): The maximum size of each chunk in characters. Default is 1000.
        """
        self.api_key = os.getenv("GROQ_API_KEY", None)
        assert self.api_key, "GROQ_API_KEY environment variable is not set"
        self.client = AsyncGroq(
            api_key=self.api_key,
        )
        self.model_name = os.getenv("SUMMARIZER_MODEL_NAME", "llama3-8b-8192")
        self.max_chunk_size = max_chunk_size
        self.max_tokens = 8000

    async def split_in_chunks(self, transcript: str) -> List[str]:
        """
        Split the transcript into smaller chunks based on the max_chunk_size.

        Args:
            transcript (str): The full transcript text to be summarized.

        Returns:
            list: A list of strings, where each string represents a chunk of the transcript.
        """
        paragraphs = re.split(r"\n{2,}", transcript)
        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 1 <= self.max_chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return [chunk for chunk in chunks if chunk]

    async def summarize_chunk(self, chunk: str, language) -> str:
        """
        Summarize a chunk of the transcript using the language model API.

        Args:
            chunk (str): A chunk of the transcript text to be summarized.

        Returns:
            str: The summary of the given chunk.

        Raises:
            requests.exceptions.RequestException: If there is an error with the API request.
        """
        try:
            chat_completion = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": CHUNK_SUMMARIZER_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": "<chunk>\n\n" + chunk + "\n\n</chunk>",
                    },
                ],
                model=self.model_name,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"},
            )
            print(chat_completion.choices[0].message.content)
            response = ResponseModel.model_validate_json(
                chat_completion.choices[0].message.content
            )
        except BadRequestError as e:
            repaired_json_dict = repair_json(
                e.body["error"]["failed_generation"], return_objects=True
            )
            response = ResponseModel.model_validate(repaired_json_dict)
        except ValidationError:
            repaired_json_dict = repair_json(
                chat_completion.choices[0].message.content, return_objects=True
            )
            response = ResponseModel.model_validate(repaired_json_dict)

        return response.summary

    async def merge_summaries(self, summaries: List[str]) -> str:
        """
        Merge the summaries of all chunks into a final summary.

        Args:
            summaries (list): A list of strings, where each string represents a summary of a chunk.

        Returns:
            str: The final summary of the entire transcript.
        """
        try:
            chat_completion = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": SUMMARIES_MERGER_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": "<summaries>\n\n"
                        + "\n\n".join(summaries)
                        + "\n\n</summaries>",
                    },
                ],
                model=self.model_name,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"},
            )

            print(chat_completion.choices[0].message.content)
            response = ResponseModel.model_validate_json(
                chat_completion.choices[0].message.content
            )
        except BadRequestError as e:
            repaired_json_dict = repair_json(
                e.body["error"]["failed_generation"], return_objects=True
            )
            response = ResponseModel.model_validate(repaired_json_dict)
        except ValidationError:
            repaired_json_dict = repair_json(
                chat_completion.choices[0].message.content, return_objects=True
            )
            response = ResponseModel.model_validate(repaired_json_dict)

        return response.summary

    async def summarize(self, transcript: str, language) -> str:
        """
        Summarize the entire transcript by splitting it into chunks, summarizing each chunk, and combining the summaries.

        Args:
            transcript (str): The full transcript text to be summarized.

        Returns:
            str: The final summary of the entire transcript.
        """
        print("Summarizing the transcript")

        chunks = await self.split_in_chunks(transcript)

        print(f"Summarizing {len(chunks)} chunks separately")
        chunk_coroutines = [
            self.summarize_chunk(chunk, language) for chunk in chunks
        ]
        summaries = await asyncio.gather(*chunk_coroutines)

        print("Merging the summaries chunks into one summary")
        final_summary = await self.merge_summaries(summaries)

        return final_summary
