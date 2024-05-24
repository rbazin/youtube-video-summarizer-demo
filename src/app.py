import gradio as gr
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import PlainTextResponse
from redis.asyncio import Redis

import os
import hmac
import hashlib
import subprocess
from time import time

from src.video_downloader import AsyncVideoDownloader
from src.transcript_summarizer import AsyncTranscriptSummarizer

downloader = AsyncVideoDownloader()
summarizer = AsyncTranscriptSummarizer()
redis_client = Redis(host="redis-ytb-summarizer", port=6379, db=0)


def validate_request(url):
    if not url.startswith("https://www.youtube.com/"):
        return False
    return True


async def summarize(url, language):
    start = time()

    if not validate_request(url):
        raise gr.Error("Invalid YouTube URL. Please enter a valid YouTube URL.")

    video_id = await downloader.get_video_id(url)

    language = language.lower()
    language_codes = {"french": "fr", "english": "en"}

    cached_summary = await redis_client.get(f"{video_id}_summary")
    if cached_summary:
        print("Cached summary retrieved")
        return cached_summary.decode("utf-8")

    cached_transcript = await redis_client.get(f"{video_id}_transcript")
    if cached_transcript:
        transcript = cached_transcript.decode("utf-8")
        print("Cached transcript retrieved")
    else:
        try:
            transcript = await downloader.get_transcript(url, language_codes[language])
            await redis_client.set(f"{video_id}_transcript", transcript)
        except Exception:
            raise gr.Error(
                f"An error occurred while fetching or generating the transcript of the video."
            )

    try:
        summary = await summarizer.summarize(transcript, language_codes[language])
        await redis_client.set(f"{video_id}_summary", summary)
    except Exception:
        raise gr.Error(
            f"An error occurred while summarizing the transcript of the video."
        )

    end = time()

    print(f"Total time to process request: {end - start:.2f}s")

    return summary


def gradio_app(use_queue=True):
    url = gr.Textbox(
        label="Enter the YouTube URL", placeholder="https://www.youtube.com/watch?v=..."
    )
    language = gr.Radio(
        ["French", "English"],
        label="Please select the language of the video",
        value="English",
    )
    output = gr.Markdown()

    interface = gr.Interface(
        fn=summarize,
        inputs=[url, language],
        outputs=output,
        title="YouTube Video Summarizer",
        description="Enter a YouTube URL and select the language to summarize the video.",
        allow_flagging="never",
        css="footer {display: none !important}",
    )

    if use_queue:
        interface.queue(default_concurrency_limit=None)

    return interface


app = FastAPI()


@app.post("/deployment-webhook")
async def handle_webhook(request: Request):

    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Signature missing"
        )

    payload = await request.body()

    secret_key = os.getenv("DEPLOYMENT_SECRET_KEY", None)
    if not secret_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Automatic deployment not configured",
        )

    expected_signature = (
        "sha256=" + hmac.new(secret_key.encode(), payload, hashlib.sha256).hexdigest()
    )
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature"
        )

    deployment_script = os.getenv("DEPLOYMENT_SCRIPT", None)
    if not deployment_script or not os.path.exists(deployment_script):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Automatic deployment not configured",
        )

    subprocess.Popen([deployment_script])

    return PlainTextResponse("Deployment triggered", status_code=status.HTTP_200_OK)


@app.get("/health-check")
def health_check():
    return {"message": "The app is properly running."}


@app.get("/summarize")
async def summarize_endpoint(url: str, language: str):
    return await summarize(url, language)


app = gr.mount_gradio_app(
    app, gradio_app(), path="/ytb-summarizer", root_path="/ytb-summarizer"
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
