const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--ignore-certificate-errors']
  });

  const page = await browser.newPage();

  // Собираем все ошибки консоли
  const consoleMessages = [];
  page.on('console', msg => {
    consoleMessages.push({
      type: msg.type(),
      text: msg.text(),
      location: msg.location()
    });
  });

  // Собираем ошибки запросов
  const failedRequests = [];
  page.on('requestfailed', request => {
    failedRequests.push({
      url: request.url(),
      failure: request.failure()
    });
  });

  // Собираем ответы с ошибками
  const errorResponses = [];
  page.on('response', response => {
    if (response.status() >= 400) {
      errorResponses.push({
        url: response.url(),
        status: response.status(),
        statusText: response.statusText()
      });
    }
  });

  console.log('🌐 Открываю страницу: https://nikolaevcodev.ru/admin/notifications\n');

  try {
    // Переходим на страницу уведомлений
    await page.goto('https://nikolaevcodev.ru/admin/notifications', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    // Ждем 3 секунды для загрузки всех скриптов
    await new Promise(resolve => setTimeout(resolve, 3000));

    console.log('✅ Страница загружена\n');

    // Вывод результатов
    console.log('=== CONSOLE MESSAGES ===');
    if (consoleMessages.length === 0) {
      console.log('✅ Нет сообщений в консоли\n');
    } else {
      consoleMessages.forEach((msg, i) => {
        console.log(`[${i + 1}] ${msg.type.toUpperCase()}: ${msg.text}`);
        if (msg.location && msg.location.url) {
          console.log(`    Location: ${msg.location.url}:${msg.location.lineNumber}`);
        }
      });
      console.log('');
    }

    console.log('=== FAILED REQUESTS ===');
    if (failedRequests.length === 0) {
      console.log('✅ Нет проваленных запросов\n');
    } else {
      failedRequests.forEach((req, i) => {
        console.log(`[${i + 1}] ${req.url}`);
        console.log(`    Failure: ${req.failure.errorText}\n`);
      });
    }

    console.log('=== HTTP ERROR RESPONSES (4xx, 5xx) ===');
    if (errorResponses.length === 0) {
      console.log('✅ Нет ошибок HTTP\n');
    } else {
      errorResponses.forEach((res, i) => {
        console.log(`[${i + 1}] ${res.status} ${res.statusText}`);
        console.log(`    URL: ${res.url}\n`);
      });
    }

    // Также проверим есть ли ошибки в самом HTML
    const pageErrors = await page.evaluate(() => {
      const errors = [];
      // Проверяем есть ли в DOM элементы с ошибками
      const errorElements = document.querySelectorAll('[class*="error"], [class*="Error"]');
      errorElements.forEach(el => {
        if (el.textContent.trim()) {
          errors.push(el.textContent.trim());
        }
      });
      return errors;
    });

    console.log('=== PAGE ERROR ELEMENTS ===');
    if (pageErrors.length === 0) {
      console.log('✅ Нет элементов с ошибками на странице\n');
    } else {
      pageErrors.forEach((err, i) => {
        console.log(`[${i + 1}] ${err}\n`);
      });
    }

  } catch (error) {
    console.error('❌ Ошибка при загрузке страницы:', error.message);
  }

  await browser.close();
})();
