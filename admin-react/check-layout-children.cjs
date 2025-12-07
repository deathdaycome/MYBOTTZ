const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  
  await page.goto('http://localhost:5173/tasks', { waitUntil: 'networkidle0' });
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  const structure = await page.evaluate(() => {
    const layoutDiv = document.querySelector('.min-h-screen');
    const children = Array.from(layoutDiv.children);
    
    return children.map((el, idx) => ({
      index: idx,
      tag: el.tagName,
      classes: el.className.substring(0, 100),
      height: el.offsetHeight,
      top: el.getBoundingClientRect().top,
      bottom: el.getBoundingClientRect().bottom,
      position: window.getComputedStyle(el).position
    }));
  });
  
  console.log('=== LAYOUT DIV CHILDREN ===');
  structure.forEach(el => console.log(JSON.stringify(el, null, 2)));
  
  await browser.close();
})();
