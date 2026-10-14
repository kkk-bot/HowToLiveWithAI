// Local VM interaction checks; this is not a real-browser test.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const path=require('node:path');
const root=path.resolve(__dirname,'..')+path.sep;
function makeElement(tag,id,open=false){const classes=new Set();return {tagName:tag,id,value:'',textContent:'',open,parentElement:null,dataset:{},events:{},scrolled:false,classList:{toggle(name,on){if(on)classes.add(name);else classes.delete(name)},contains(name){return classes.has(name)}},addEventListener(name,fn){this.events[name]=fn},scrollIntoView(){this.scrolled=true}}}
function fixture(file,search='',hash=''){
 const html=fs.readFileSync(root+file,'utf8'),script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
 const main=makeElement('MAIN','main'),nodes={search:makeElement('INPUT','search'),'chapter-filter':makeElement('SELECT','chapter-filter'),count:makeElement('SPAN','count'),empty:makeElement('P','empty'),reset:makeElement('BUTTON','reset'),print:makeElement('BUTTON','print')};
 const details=[...html.matchAll(/<details id="([^"]+)"( open)?>/g)].map(m=>makeElement('DETAILS',m[1],!!m[2]));details.forEach(d=>d.parentElement=main);
 const entries=[...html.matchAll(/<article class="entry" id="entry-([^\"]+)" data-chapter="(\d+)">([\s\S]*?)<\/article>/g)].map(m=>{const e=makeElement('ARTICLE','entry-'+m[1]);e.dataset.chapter=m[2];e.textContent=m[3].replace(/<[^>]*>/g,'');return e});
 const sections=[...new Set(entries.map(e=>e.dataset.chapter))].map(id=>{const s=makeElement('SECTION','chapter-'+id);s.parentElement=main;s.querySelectorAll=()=>entries.filter(e=>e.dataset.chapter===id);for(const e of s.querySelectorAll())e.parentElement=s;return s});
 const anchor=makeElement('A','r22');anchor.parentElement=details.find(d=>d.id==='appendix-d');
 const ids=Object.fromEntries([...details,...sections,...entries,anchor].map(e=>[e.id,e]));
 const window={events:{},printCalls:0,addEventListener(name,fn){this.events[name]=fn},print(){this.printCalls++}};
 const location={hash,search,pathname:'/'+file},history={last:null,replaceState(a,b,url){this.last=url}};
 const document={events:{},addEventListener(name,fn){this.events[name]=fn},body:makeElement('BODY','body'),querySelector(s){return nodes[s.slice(1)]},querySelectorAll(s){return s==='.entry'?entries:s==='[data-section]'?sections:s==='details'?details:[]},getElementById(id){return ids[id]}};
 document.body.classList.toggle('continuous',file==='阅读全文.html');
 vm.runInNewContext(script,{window,document,location,history,URLSearchParams,requestAnimationFrame:fn=>fn()});
 return{html,nodes,details,entries,sections,window,document,location,history,ids,filterQuery(value){nodes.search.value=value;nodes.search.events.input()},filterChapter(value){nodes['chapter-filter'].value=value;nodes['chapter-filter'].events.change()},visible(){return entries.filter(e=>!e.classList.contains('hidden'))},hash(value){location.hash=value;window.events.hashchange()}};
}
let checks=0;function ok(fn){fn();checks++}
for(const file of ['index.html','阅读全文.html']){
 let f=fixture(file);
 ok(()=>assert.equal(f.visible().length,29));
 ok(()=>{f.filterChapter('4');assert.deepEqual(f.visible().map(e=>e.id),['entry-4.1','entry-4.2','entry-4.3','entry-4.4','entry-4.5'])});
 ok(()=>{f.filterQuery('独立 解释');assert(f.visible().length>0);assert(f.visible().every(e=>e.textContent.includes('独立')&&e.textContent.includes('解释')))});
 ok(()=>{f.filterQuery('不存在的检索词xyz');assert.equal(f.visible().length,0);assert.equal(f.nodes.empty.classList.contains('hidden'),false)});
 ok(()=>{f.nodes.reset.events.click();assert.equal(f.visible().length,29);assert.equal(f.nodes.empty.classList.contains('hidden'),true)});
 ok(()=>{f=fixture(file,'?chapter=4&q=独立');if(file==='index.html'){assert(f.visible().length>0);assert(f.visible().every(e=>e.dataset.chapter==='4'&&e.textContent.includes('独立')))}else{assert.equal(f.visible().length,29);assert.equal(f.nodes.search.value,'');assert.equal(f.nodes['chapter-filter'].value,'')}});
 ok(()=>{f=fixture(file,'?q=不存在','#appendix-b');assert.equal(f.ids['appendix-b'].open,true);assert(f.ids['appendix-b'].scrolled);assert.equal(f.visible().length,29)});
 ok(()=>{f=fixture(file);f.hash('#r22');assert(f.ids.r22.parentElement.open);assert(f.ids.r22.scrolled)});
 ok(()=>{f.filterChapter('9');f.hash('#entry-1.1');assert(f.visible().length===29&&f.ids['entry-1.1'].scrolled)});
 ok(()=>{f.hash('#%E0%A4%A');f.hash('#missing');assert.equal(f.visible().length,29)});
 ok(()=>{f=fixture(file);const before=f.details.map(d=>d.open);f.window.events.beforeprint();assert(f.details.every(d=>d.open));f.window.events.afterprint();assert.deepEqual(f.details.map(d=>d.open),before)});
 ok(()=>{const before=f.details.map(d=>d.open);f.nodes.print.events.click();assert.equal(f.window.printCalls,1);assert(f.details.every(d=>d.open));f.window.events.beforeprint();f.window.events.afterprint();assert.deepEqual(f.details.map(d=>d.open),before)});
 ok(()=>{const css=f.html.match(/<style>([\s\S]*?)<\/style>/)[1];const printing=css.slice(css.indexOf('@media print'));assert(printing.includes('#empty{display:none!important}'));assert(!printing.includes('.hidden{display:block!important}details'));assert(printing.includes('[data-section].hidden,.entry.hidden{display:block!important}'))});
 if(file==='阅读全文.html')ok(()=>assert(f.details.every(d=>d.open)));
}


function click(f,href,extra={}){const link={getAttribute:()=>href};const event={target:{closest:()=>link},button:0,defaultPrevented:false,preventDefault(){this.defaultPrevented=true},...extra};f.document.events.click(event);return event}
for(const file of ['index.html','阅读全文.html']){
 ok(()=>{const f=fixture(file,'','#entry-1.1');f.filterQuery('不存在的关键词xyz');assert.equal(f.ids['entry-1.1'].classList.contains('hidden'),true);const e=click(f,'#entry-1.1');assert(e.defaultPrevented);assert.equal(f.visible().length,29);assert.equal(f.ids['entry-1.1'].classList.contains('hidden'),false);assert(f.ids['entry-1.1'].scrolled)});
 ok(()=>{const f=fixture(file);const e=click(f,'#appendix-b');assert(e.defaultPrevented);assert(f.ids['appendix-b'].open);assert(f.ids['appendix-b'].scrolled)});
 ok(()=>{const f=fixture(file,'','#appendix-d');f.ids['appendix-d'].open=false;click(f,'#appendix-d');assert(f.ids['appendix-d'].open)});
 ok(()=>{const f=fixture(file);f.filterQuery('不存在的关键词xyz');const e=click(f,'#entry-1.1',{ctrlKey:true});assert(!e.defaultPrevented);assert.equal(f.visible().length,0)});
 ok(()=>{const f=fixture(file);click(f,'#missing');click(f,'#%E0%A4%A');assert.equal(f.visible().length,29)});
 ok(()=>{const f=fixture(file);f.document.events.click({target:{},button:0});assert.equal(f.visible().length,29)});
 ok(()=>{const f=fixture(file);assert.equal((f.html.match(/<h1>/g)||[]).length,1);assert(f.html.includes(' / ${entries.length} 节'))});
}
ok(()=>{const f=fixture('阅读全文.html','?q=不存在的关键词xyz&chapter=99');assert.equal(f.visible().length,29);assert(f.details.every(d=>d.open));assert(!f.history.last.includes('?'))});
console.log(`${checks} 项本地交互检查通过，包括同一锚点重入、连续版参数、修饰键和标题层级。`);
