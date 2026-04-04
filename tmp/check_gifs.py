import aiohttp
import asyncio

GIFS = {
    "hug": [
        "https://media1.tenor.com/m/X6YT2FsV3bAAAAAC/cat.gif",
        "https://media1.tenor.com/m/hCCX8oPm3S0AAAAC/don.gif",
        "https://media1.tenor.com/m/LiGTbtBFUdEAAAAC/peach-and-goma-hugging.gif",
        "https://media1.tenor.com/m/v7mBih_Zf-0AAAAC/hug.gif",
        "https://media1.tenor.com/m/6Y_fC-Kz17UAAAAC/monkey-hug-monkeys-hugging.gif"
    ],
    "kick": [
        "https://media1.tenor.com/m/T4ZAs1o6I_UAAAAC/oh-yeah-high-kick.gif",
        "https://media1.tenor.com/m/0v_5S9H1R9YAAAAC/asdf-movie-punt.gif",
        "https://media1.tenor.com/m/6z7-Z_y_I20AAAAC/bubu-kick-dudu.gif",
        "https://media1.tenor.com/m/sP57H0qA52MAAAAC/milk-and-mocha.gif",
        "https://media1.tenor.com/m/rXW_XqZ2M-YAAAAC/kick.gif"
    ],
    "slap": [
        "https://media1.tenor.com/m/MrhME3n9Z2UAAAAC/dungeong.gif",
        "https://media1.tenor.com/m/tMVS_yML7t0AAAAC/slap-slaps.gif",
        "https://media1.tenor.com/m/OY6vL9fL8P0AAAAC/cats-cat-slap.gif",
        "https://media1.tenor.com/m/8Y6E-L_Q-p0AAAAC/taiga-toradora.gif",
        "https://media1.tenor.com/m/4Y6vL9fL8P0AAAAC/slap.gif"
    ],
    "kiss": [
        "https://media1.tenor.com/m/L-grpASXygAAAAC/bubuiak14kiss1.gif",
        "https://media1.tenor.com/m/X6vL9fL8P0AAAAC/cosytales.gif",
        "https://media1.tenor.com/m/Z6vL9fL8P0AAAAC/puuung.gif",
        "https://media1.tenor.com/m/W6vL9fL8P0AAAAC/puuung-kiss.gif"
    ],
    "punch": [
        "https://media1.tenor.com/m/nF_grpASXygAAAAC/bubu-dudu.gif",
        "https://media1.tenor.com/m/RiLHXlSdFd4AAAAC/facepunch-punch.gif",
        "https://media1.tenor.com/m/6Cp5tiRwh-YAAAAC/meme-memes.gif",
        "https://media1.tenor.com/m/8Cp5tiRwh-YAAAAC/punch.gif"
    ]
}

async def check_url(session, category, url):
    try:
        async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5) as resp:
            print(f"[{category}] {url} -> {resp.status} ({resp.content_type})")
            return resp.status == 200 and resp.content_type.startswith("image")
    except Exception as e:
        print(f"[{category}] {url} -> FAILED: {e}")
        return False

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for cat, urls in GIFS.items():
            for url in urls:
                tasks.append(check_url(session, cat, url))
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
