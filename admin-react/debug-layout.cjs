const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  
  await page.setViewport({ width: 1920, height: 1080 });
  
  await page.goto('http://localhost:5173/tasks', { waitUntil: 'networkidle0', timeout: 15000 });
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  const measurements = await page.evaluate(() => {
    const main = document.querySelector('main');
    const topBar = document.querySelector('main > div');
    const sidebar = document.querySelector('aside');
    
    return {
      mainTop: main ? main.getBoundingClientRect().top : null,
      topBarTop: topBar ? topBar.getBoundingClientRect().top : null,
      sidebarTransform: sidebar ? window.getComputedStyle(sidebar).transform : null,
      bodyPadding: window.getComputedStyle(document.body).paddingTop,
    };
  });
  
  console.log('=== LAYOUT MEASUREMENTS ===');
  console.log(JSON.stringify(measurements, null, 2));
  
  await browser.close();
})();
