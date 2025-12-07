const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();

  // Слушаем console.log из браузера
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    console.log(`[BROWSER ${type.toUpperCase()}]:`, text);
  });

  // Слушаем ошибки
  page.on('pageerror', error => {
    console.error('[BROWSER ERROR]:', error.message);
  });

  // Слушаем отказы в загрузке ресурсов
  page.on('requestfailed', request => {
    console.error('[REQUEST FAILED]:', request.url(), request.failure().errorText);
  });

  try {
    console.log('Открываем http://localhost:5174...');
    await page.goto('http://localhost:5174', {
      waitUntil: 'networkidle0',
      timeout: 10000
    });

    // Ждем немного
    await page.waitForTimeout(2000);

    // Проверяем содержимое body
    const bodyHTML = await page.evaluate(() => document.body.innerHTML);
    console.log('\n[BODY CONTENT LENGTH]:', bodyHTML.length);

    if (bodyHTML.length < 100) {
      console.log('[BODY CONTENT]:', bodyHTML);
    } else {
      console.log('[BODY CONTENT (first 500 chars)]:', bodyHTML.substring(0, 500));
    }

    // Проверяем наличие root элемента
    const rootElement = await page.$('#root');
    if (rootElement) {
      const rootHTML = await page.evaluate(el => el.innerHTML, rootElement);
      console.log('\n[ROOT ELEMENT LENGTH]:', rootHTML.length);

      if (rootHTML.length < 100) {
        console.log('[ROOT IS EMPTY OR MINIMAL]');
        console.log('[ROOT CONTENT]:', rootHTML);
      }
    } else {
      console.log('\n[ROOT ELEMENT NOT FOUND!]');
    }

    // Делаем скриншот
    await page.screenshot({ path: '/Users/ivan/Desktop/СРМ РЕАКТ/admin-react/screenshot.png' });
    console.log('\nСкриншот сохранен в screenshot.png');

  } catch (error) {
    console.error('Ошибка:', error.message);
  } finally {
    await browser.close();
  }
})();
