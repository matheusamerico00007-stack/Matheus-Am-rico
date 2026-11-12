const { chromium } = require('playwright');
(async()=>{const [,,dir]=process.argv;const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
await p.goto('file://'+dir+'/capa.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
for(const id of ['v1','v2']){await p.evaluate(id=>{document.querySelectorAll('.v').forEach(e=>e.style.display='none');document.getElementById(id).style.display='block'},id);
await p.screenshot({path:`${dir}/capa_${id}.png`});}await b.close();})();
