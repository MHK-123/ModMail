import aiohttp
import asyncio

TEST_URLS = [
    "https://media.tenor.com/LiGTbtBFUdEAAAAC/peach-and-goma-hugging.gif", # Fallback
    "https://media.tenor.com/9C0D3_C-GBAAAAAC/hug-love.gif",
    "https://media.tenor.com/6XyU-8q3N-MAAAAC/hugs-peach-goma.gif",
    "https://media.tenor.com/vH9YOnk9t24AAAAC/kick-funny.gif",
    "https://media.tenor.com/6z7-Z_y_I20AAAAC/bubu-kick-dudu.gif",
    "https://media.tenor.com/tMVS_yML7t0AAAAC/slap-slaps.gif",
]

async def check_url(session, url):
    try:
        async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5) as resp:
            print(f"{url} -> {resp.status} ({resp.content_type})")
            return resp.status == 200 and resp.content_type.startswith("image")
    except Exception as e:
        print(f"{url} -> FAILED: {e}")
        return False

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [check_url(session, url) for url in TEST_URLS]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
