const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });

  await page.goto('http://localhost:5173/tasks', { waitUntil: 'networkidle0' });
  await new Promise(resolve => setTimeout(resolve, 2000));

  const columnInfo = await page.evaluate(() => {
    // Находим все колонки с задачами
    const columns = Array.from(document.querySelectorAll('.overflow-y-auto.custom-scrollbar'));

    return columns.map((col, index) => {
      const styles = window.getComputedStyle(col);
      return {
        columnIndex: index,
        overflow: styles.overflow,
        overflowY: styles.overflowY,
        maxHeight: styles.maxHeight,
        scrollHeight: col.scrollHeight,
        clientHeight: col.clientHeight,
        canScroll: col.scrollHeight > col.clientHeight,
        currentScrollTop: col.scrollTop
      };
    });
  });

  console.log('\n=== TASK COLUMNS INFO ===\n');
  console.log(JSON.stringify(columnInfo, null, 2));

  if (columnInfo.length > 0) {
    // Попытка прокрутить первую колонку
    await page.evaluate(() => {
      const firstColumn = document.querySelector('.overflow-y-auto.custom-scrollbar');
      if (firstColumn) {
        firstColumn.scrollTop = 300;
      }
    });

    await new Promise(resolve => setTimeout(resolve, 500));

    const scrollResult = await page.evaluate(() => {
      const firstColumn = document.querySelector('.overflow-y-auto.custom-scrollbar');
      return firstColumn ? firstColumn.scrollTop : null;
    });

    console.log(`\n=== After scrolling first column to 300: scrollTop = ${scrollResult} ===`);
  }

  await browser.close();
})();
