const { Telegraf } = require('telegraf');

const puppeteer = require('puppeteer');

const bot = new Telegraf('5978465545:AAEWxuoeJIpAY60-qOG3O9lndLUEW62i3rI');

async function getJoke() {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto('https://icanhazdadjoke.com/')
  const joke = await page.$eval('body > section > div > div:nth-child(2) > div > div > p', (element) => element.textContent);
  await browser.close();

  return joke;
}

bot.command('joke', async (ctx) => {
  try {
    const joke = await getJoke();
    ctx.reply(joke);
  } catch (error) {
    console.error(error);
    ctx.reply('Произошла ошибка');
  }
});

bot.launch();