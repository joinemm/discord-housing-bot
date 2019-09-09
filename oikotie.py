import random
from bs4 import BeautifulSoup
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from discord.ext import commands
import yaml
import asyncio

firefox_profile = webdriver.FirefoxProfile()
# firefox_profile.set_preference('permissions.default.image', 2)
# firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options, firefox_profile=firefox_profile)


class Oikotie(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.use_useragent = False
        self.running = False
        self.settings = self.get_settings()

    async def on_ready(self):
        if not self.running:
            print("Running loop")
            await self.refresh_loop()

    @commands.command(name="houses")
    @commands.is_owner()
    async def get_houses(self, ctx, amount=5):
        for link in self.emulator()[:int(amount)]:
            await ctx.send(link)

    @commands.command(name="location")
    @commands.is_owner()
    async def set_location(self, ctx, *, locationstring):
        self.settings['location'] = locationstring
        self.write_settings()
        await ctx.send(f"location string set to `{locationstring}`")

    @commands.command(name="channel")
    @commands.is_owner()
    async def set_channel(self, ctx, channel):
        self.settings['channel'] = int(channel)
        self.write_settings()
        await ctx.send(f"channel set to <#{channel}>")

    @commands.command(name="settings")
    @commands.is_owner()
    async def view_settings(self, ctx):
        await ctx.send(f"```{self.settings}```")

    async def refresh_loop(self):
        if self.running:
            print("Destroyed duplicate loop instance")
            return
        while True:
            for link in self.emulator():
                house_id = int(link.split('/')[-1])
                if house_id not in self.settings.get('house_ids'):
                    print("new house", house_id)
                    self.client.get_channel(self.settings.get('channel').send(link))
                    self.settings['house_ids'].append(house_id)
            print("sleeping for 1 hour")
            await asyncio.sleep(3600)

    def get_settings(self):
        with open("settings.yaml", "r") as f:
            return yaml.safe_load(f)

    def write_settings(self):
        with open("settings.yaml", "w", encoding='utf8') as f:
            yaml.dump(self.settings, f, default_flow_style=False, allow_unicode=True)

    def emulator(self):
        url = 'https://asunnot.oikotie.fi/vuokrattavat-asunnot?pagination=1&cardType=101&' \
              f'locations={self.settings.get("location")}'

        if self.use_useragent:
            driver.header_overrides = {
                "User-Agent": get_useragent()
            }

        driver.get(url)
        source = driver.find_element_by_xpath("//body").get_attribute('outerHTML')
        soup = BeautifulSoup(source, "lxml")
        cards = soup.find_all('a', {'class': 'ot-card'})
        return [card.get('href') for card in cards]


def setup(client):
    client.add_cog(Oikotie(client))


def get_useragent():
    with open('useragents.txt', 'r') as f:
        return random.choice(f.readlines()).rstrip()
