const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });

  await page.goto('http://localhost:5173/tasks', { waitUntil: 'networkidle0' });
  await new Promise(resolve => setTimeout(resolve, 2000));

  const scrollInfo = await page.evaluate(() => {
    const body = document.body;
    const html = document.documentElement;

    return {
      bodyHeight: body.scrollHeight,
      viewportHeight: window.innerHeight,
      canScroll: body.scrollHeight > window.innerHeight,
      bodyOverflow: window.getComputedStyle(body).overflow,
      bodyOverflowY: window.getComputedStyle(body).overflowY,
      htmlOverflow: window.getComputedStyle(html).overflow,
      htmlOverflowY: window.getComputedStyle(html).overflowY,
      currentScrollY: window.scrollY,
      maxScroll: body.scrollHeight - window.innerHeight
    };
  });

  console.log('\n=== SCROLL INFO BEFORE ===');
  console.log(JSON.stringify(scrollInfo, null, 2));

  // Попытка прокрутить
  await page.evaluate(() => {
    window.scrollTo(0, 500);
  });

  await new Promise(resolve => setTimeout(resolve, 500));

  const scrollAfter = await page.evaluate(() => {
    return {
      scrollY: window.scrollY,
      scrolled: window.scrollY > 0
    };
  });

  console.log('\n=== SCROLL INFO AFTER (tried to scroll to 500) ===');
  console.log(JSON.stringify(scrollAfter, null, 2));

  await browser.close();
})();
