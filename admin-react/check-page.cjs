const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();

  page.on('console', msg => {
    const type = msg.type();
    console.log('[BROWSER ' + type + ']:', msg.text());
  });

  page.on('pageerror', error => console.error('[ERROR]:', error.message));

  try {
    console.log('B:@K205< http://localhost:5174...');
    await page.goto('http://localhost:5174', {
      waitUntil: 'networkidle0',
      timeout: 10000
    });

    await new Promise(resolve => setTimeout(resolve, 3000));

    const bodyHTML = await page.evaluate(() => document.body.innerHTML);
    console.log('\n[!" &  #, 4;8=0 HTML]:', bodyHTML.length);

    const rootElement = await page.$('#root');
    if (rootElement) {
      const rootHTML = await page.evaluate(el => el.innerHTML, rootElement);
      console.log('[ROOT M;5<5=B 70?>;=5=, 4;8=0]:', rootHTML.length);
      if (rootHTML.length > 100) {
        console.log(' @8;>65=85 CA?5H=> 703@C78;>AL!');
      } else {
        console.log('  ROOT ?CAB>9');
      }
    }

    await page.screenshot({ path: '/Users/ivan/Desktop/!   "/admin-react/screenshot.png' });
    console.log('\n!:@8=H>B A>E@0=5=: screenshot.png');

  } catch (error) {
    console.error('H81:0:', error.message);
  } finally {
    await browser.close();
  }
})();
