const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });

  await page.goto('http://localhost:5173/tasks', { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 2000));

  const info = await page.evaluate(() => {
    const columns = document.querySelectorAll('.flex-shrink-0.w-\\[340px\\]');
    const taskContainers = Array.from(columns).map(col => {
      const taskDiv = col.querySelector('.space-y-3');
      if (!taskDiv) return null;

      const styles = window.getComputedStyle(taskDiv);
      return {
        className: taskDiv.className,
        minHeight: styles.minHeight,
        maxHeight: styles.maxHeight,
        offsetHeight: taskDiv.offsetHeight,
        scrollHeight: taskDiv.scrollHeight
      };
    }).filter(Boolean);

    return {
      taskContainers,
      bodyHeight: document.body.scrollHeight,
      viewportHeight: window.innerHeight,
      maxScroll: document.body.scrollHeight - window.innerHeight
    };
  });

  console.log('\n=== COLUMN INFO ===\n');
  console.log(JSON.stringify(info, null, 2));

  await browser.close();
})();
