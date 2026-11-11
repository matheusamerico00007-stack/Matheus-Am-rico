const { chromium } = require('playwright');
(async()=>{
  const [,,dir,id,dur,fps]=process.argv;
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  await p.goto('file://'+dir+'/cards.html'); await p.evaluate(()=>document.fonts.ready);
  await p.evaluate(id=>{document.getElementById(id).style.display='block'},id);
  await p.evaluate(()=>document.getAnimations().forEach(a=>a.pause()));
  const n=Math.round(dur*fps);
  for(let i=0;i<n;i++){
    const t=i/fps*1000;
    await p.evaluate(t=>document.getAnimations().forEach(a=>{a.currentTime=t}),t);
    await p.screenshot({path:`${dir}/${id}_${String(i).padStart(4,'0')}.png`});
  }
  await b.close();
})();
