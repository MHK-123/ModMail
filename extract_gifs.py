import asyncio
import aiohttp
import re

TENOR_URLS = [
    "https://tenor.com/en-GB/view/cat-gif-6892218099699146160",
    "https://tenor.com/en-GB/view/don-gif-9520776680112053549",
    "https://tenor.com/en-GB/view/peach-and-goma-hugging-love-cute-gif-3324100104126026193",
    "https://tenor.com/en-GB/view/hug-gif-16145194991064460629",
    "https://tenor.com/en-GB/view/monkey-hug-monkeys-hugging-golden-monkeys-gif-11103289529249683769",
    "https://tenor.com/en-GB/view/oh-yeah-high-kick-take-down-fight-gif-14272509",
    "https://tenor.com/en-GB/view/asdf-movie-punt-kick-donewiththis-gif-26537188",
    "https://tenor.com/en-GB/view/bubu-kick-dudu-bubu-angry-bubu-dudu-love-gif-5644488481606895836",
    "https://tenor.com/en-GB/view/milk-and-mocha-gif-16310787379898746257",
    "https://tenor.com/en-GB/view/kickers-caught-gif-7775692",
    "https://tenor.com/en-GB/view/dungeong-gif-3654754744145897317",
    "https://tenor.com/en-GB/view/slap-slaps-enough-stop-stop-it-gif-13025908752997150429",
    "https://tenor.com/en-GB/view/cats-cat-slap-slap-gif-2895385951685947789",
    "https://tenor.com/en-GB/view/taiga-toradora-fast-slap-slap-baka-gif-11264049955690132886",
    "https://tenor.com/en-GB/view/slap-gif-4486401254555935391",
    "https://tenor.com/en-GB/view/bubuiak14kiss1-gif-13338760645080724504",
    "https://tenor.com/en-GB/view/cosytales-love-chubby-valentine-shy-gif-15963472677482031132",
    "https://tenor.com/en-GB/view/puuung-kiss-puuung-gif-14695589765038452485",
    "https://tenor.com/en-GB/view/puuung-kiss-my-sonic-goober-gif-8039438698073654471",
    "https://tenor.com/en-GB/view/bubu-dudu-bubu-dudu-motki-motki-bubu-gif-11267971833050324776",
    "https://tenor.com/en-GB/view/pepe-smash-punch-smile-gif-16883739",
    "https://tenor.com/en-GB/view/facepunch-punch-minions-fine-happy-gif-5053820939823551966",
    "https://tenor.com/en-GB/view/meme-memes-memes2022funny-meme-face-punch-gif-25436787"
]

async def get_direct_url(session, url):
    try:
        async with session.get(url) as response:
            text = await response.text()
            # Look for og:image which is usually the direct GIF URL
            match = re.search(r'<meta property="og:image" content="(https://media[0-9]*\.tenor\.com/[^"]+\.gif)"', text)
            if match:
                return match.group(1)
            # Fallback to search for any tenor media link if og:image fails
            match = re.search(r'(https://media[0-9]*\.tenor\.com/[^"]+\.gif)', text)
            return match.group(1) if match else f"ERROR: {url}"
    except Exception as e:
        return f"EXCEPTION: {url} ({e})"

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [get_direct_url(session, url) for url in TENOR_URLS]
        results = await asyncio.gather(*tasks)
        print("BEGIN_URLS")
        for i, res in enumerate(results):
            print(f"{i+1}///{res}")
        print("END_URLS")

if __name__ == "__main__":
    asyncio.run(main())
