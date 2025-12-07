const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });

  await page.goto('http://localhost:5173/tasks', { waitUntil: 'networkidle0' });
  await new Promise(resolve => setTimeout(resolve, 2000));

  const diagnosis = await page.evaluate(() => {
    const getElementInfo = (selector, name) => {
      const el = document.querySelector(selector);
      if (!el) return { name, found: false };

      const styles = window.getComputedStyle(el);
      const rect = el.getBoundingClientRect();

      return {
        name,
        found: true,
        overflow: styles.overflow,
        overflowX: styles.overflowX,
        overflowY: styles.overflowY,
        height: styles.height,
        scrollHeight: el.scrollHeight,
        clientHeight: el.clientHeight,
        canScrollVertically: el.scrollHeight > el.clientHeight,
        position: styles.position,
        top: rect.top,
        bottom: rect.bottom
      };
    };

    return {
      html: getElementInfo('html', 'HTML'),
      body: getElementInfo('body', 'BODY'),
      root: getElementInfo('#root', 'Root div'),
      layoutDiv: getElementInfo('#root > div', 'Layout wrapper'),
      main: getElementInfo('main', 'Main element'),
      tasksPage: getElementInfo('main > div', 'Tasks page container'),

      viewport: {
        width: window.innerWidth,
        height: window.innerHeight,
        scrollY: window.scrollY,
        scrollX: window.scrollX
      }
    };
  });

  console.log('\n=== OVERFLOW DIAGNOSIS ===\n');
  console.log(JSON.stringify(diagnosis, null, 2));

  // Попробуем прокрутить разными способами
  await page.evaluate(() => window.scrollBy(0, 300));
  await new Promise(resolve => setTimeout(resolve, 300));

  const scrollTest1 = await page.evaluate(() => window.scrollY);
  console.log(`\n=== After window.scrollBy(0, 300): scrollY = ${scrollTest1} ===`);

  await page.evaluate(() => document.documentElement.scrollTop = 500);
  await new Promise(resolve => setTimeout(resolve, 300));

  const scrollTest2 = await page.evaluate(() => window.scrollY);
  console.log(`=== After documentElement.scrollTop = 500: scrollY = ${scrollTest2} ===`);

  await browser.close();
})();
