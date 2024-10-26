from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime

app = FastAPI()

# Allow CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust this if your frontend URL changes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your existing endpoint code
HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

@app.get("/top-stories")
async def get_top_stories():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(HN_TOP_STORIES_URL)
            response.raise_for_status()
            story_ids = response.json()[:10]
            stories = await get_story_details(client, story_ids)
            return stories
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="HackerNews API is unreachable.")

async def get_story_details(client, story_ids):
    stories = []
    for story_id in story_ids:
        response = await client.get(HN_ITEM_URL.format(story_id))
        story_data = response.json()
        # Append the formatted story details to the stories list
        stories.append({
            "title": story_data.get("title"),
            "author": story_data.get("by"),
            "url": story_data.get("url"),
            "score": story_data.get("score"),
            "time": datetime.fromtimestamp(story_data.get("time")).strftime('%Y-%m-%d %H:%M:%S')
        })
    return stories
