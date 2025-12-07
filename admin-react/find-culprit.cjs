const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  
  await page.goto('http://localhost:5173/tasks', { waitUntil: 'networkidle0' });
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  const structure = await page.evaluate(() => {
    const root = document.getElementById('root');
    const children = Array.from(root.children);
    
    return children.map(el => ({
      tag: el.tagName,
      classes: el.className,
      height: el.offsetHeight,
      top: el.getBoundingClientRect().top,
      styles: {
        minHeight: window.getComputedStyle(el).minHeight,
        height: window.getComputedStyle(el).height,
        display: window.getComputedStyle(el).display
      }
    }));
  });
  
  console.log('=== ROOT CHILDREN ===');
  console.log(JSON.stringify(structure, null, 2));
  
  await browser.close();
})();
