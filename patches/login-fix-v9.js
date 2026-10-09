(()=>{
if(window.__dfLoginFix)return;
const add=EventTarget.prototype.addEventListener,remove=EventTarget.prototype.removeEventListener;
const watchers=new WeakMap();
const isField=t=>t instanceof Element&&!!t.closest('input:not([type=button]):not([type=submit]),textarea,[contenteditable="true"]');
const cap=o=>typeof o==='boolean'?o:!!o?.capture;
const types=new Set(['pointerdown','pointerup','mousedown','mouseup','click','dblclick','touchstart','touchend','keydown','keyup','keypress']);
EventTarget.prototype.addEventListener=function(type,listener,options){
 if((this===window||this===document)&&types.has(type)&&listener){
  let map=watchers.get(listener);if(!map){map=new Map();watchers.set(listener,map)}
  const key=type+':'+cap(options);
  if(!map.has(key))map.set(key,function(e){if(isField(e.target))return;return typeof listener==='function'?listener.call(this,e):listener.handleEvent?.(e)});
  return add.call(this,type,map.get(key),options);
 }
 return add.call(this,type,listener,options);
};
EventTarget.prototype.removeEventListener=function(type,listener,options){return remove.call(this,type,watchers.get(listener)?.get(type+':'+cap(options))||listener,options)};
const shown=e=>e.isConnected&&e.getClientRects().length>0&&getComputedStyle(e).display!=='none'&&getComputedStyle(e).visibility!=='hidden';
const accountScope=()=>document.querySelector('.px-acctwin .acct,.px-acctwin,.acct');
const inputs=()=>Array.from((accountScope()||document).querySelectorAll('input,textarea')).filter(e=>shown(e)&&!e.disabled&&!e.readOnly&&!['submit','button','checkbox','radio','hidden','file','range','color'].includes(e.type));
const saved=new WeakMap();
const harmless=new Set(['type','value','maxlength','autocomplete','autocapitalize','spellcheck','inputmode','placeholder','required','aria-label','aria-describedby','data-df-isolated']);
function isolate(){
 let count=0;
 for(const e of inputs()){
  if(saved.has(e))continue;
  const attrs=Array.from(e.attributes).map(a=>[a.name,a.value]);
  saved.set(e,{attrs,oninput:e.oninput,onkeydown:e.onkeydown,onclick:e.onclick,onfocus:e.onfocus,onblur:e.onblur,originalClass:e.className});
  // Remove every identifier, class, name and inline event attribute while
  // retaining input semantics. acctKey is a JS property, not an HTML attribute.
  for(const a of Array.from(e.attributes))if(!harmless.has(a.name.toLowerCase()))e.removeAttribute(a.name);
  e.setAttribute('data-df-isolated','1');
  // Keep the flow's oninput bridge but avoid focus/keyboard/tap handlers on the element.
  e.onkeydown=null;e.onclick=null;e.onfocus=null;e.onblur=null;
  count++;
 }
 return count;
}
function restore(){
 let count=0;
 for(const e of inputs()){
  const s=saved.get(e);if(!s)continue;
  for(const a of Array.from(e.attributes))e.removeAttribute(a.name);
  for(const [k,v] of s.attrs)e.setAttribute(k,v);
  e.oninput=s.oninput;e.onkeydown=s.onkeydown;e.onclick=s.onclick;e.onfocus=s.onfocus;e.onblur=s.onblur;
  saved.delete(e);count++;
 }
 return count;
}
const set=(e,v)=>{
 const proto=e instanceof HTMLTextAreaElement?HTMLTextAreaElement.prototype:HTMLInputElement.prototype;
 Object.getOwnPropertyDescriptor(proto,'value').set.call(e,v);
 // Site's handler writes to account flow. Do not dispatch DOM input/change.
 if(typeof e.oninput==='function')e.oninput.call(e,new Event('input'));
};
function description(){
 return inputs().map((e,i)=>({index:i,key:e.acctKey||'',type:e.type,label:e.labels?.[0]?.textContent?.trim()||e.getAttribute('aria-label')||e.placeholder||e.name||e.type,value:e.value}));
}
function invoke(b){
 // The account flow lives in the onclick property. Calling it directly
 // prevents document/window click listeners from interpreting the action as Back.
 if(typeof b.onclick==='function'){b.onclick.call(b);return true}
 b.click();return true;
}
function findAction(kind){
 const scope=accountScope();if(!scope)return null;
 const buttons=Array.from(scope.querySelectorAll('button,input[type=submit]')).filter(shown);
 if(kind==='submit')return buttons.find(b=>b.acctKey==='act:submit')||buttons.find(b=>b.type==='submit')||buttons.find(b=>/^(sign in|log in|login|create account|register)$/i.test((b.textContent||b.value||'').trim()));
 return buttons.find(b=>new RegExp(kind==='register'?'^(create account|register|sign up)$':'^(sign in|log in|login)$','i').test((b.textContent||b.value||'').trim()));
}
function fill(values,submit){
 let descriptors=description();
 if(!Array.isArray(values)||values.length!==descriptors.length||!values.length)return false;
 for(let i=0;i<values.length;i++){
  let current=inputs(),key=descriptors[i].key;
  let e=(key?current.find(x=>x.acctKey===key):null)||current[i];
  if(!e)return false;
  set(e,String(values[i]));
 }
 if(submit){
  restore();
  const b=findAction('submit');
  if(!b||b.disabled)return false;
  return invoke(b);
 }
 return true;
}
window.__dfFocused=null;
add.call(window,'focusin',e=>{if(isField(e.target))window.__dfFocused=e.target},false);
let lastStage='',dismissed='';
function nativeStage(){
 const scope=accountScope();
 if(!scope || !shown(scope))return '';
 const keys=Array.from(scope.querySelectorAll('input')).map(e=>e.acctKey||'');
 const stage=keys.includes('field:handle')&&keys.includes('field:password')?(keys.includes('field:confirm')?'register':'login'):'';
 return stage;
}
function nativeTick(){
 const stage=nativeStage();
 if(stage!==lastStage){lastStage=stage;dismissed=''}
 if(stage&&stage!==dismissed&&stage!==announced){
  announced=stage;
  try{window.dfAccountEntry?.postMessage(stage)}catch{}
 }else if(!stage){announced=''}
}
let announced='';
function submitNative(json){
 try{
  const data=JSON.parse(json),stage=nativeStage();
  if(!stage||!data||typeof data!=='object')return false;
  const keys=stage==='register'?['handle','password','confirm']:['handle','password'];
  const elements=keys.map(k=>Array.from((accountScope()||document).querySelectorAll('input')).find(e=>e.acctKey==='field:'+k));
  if(elements.some(e=>!e))return false;
  for(let i=0;i<keys.length;i++){
   if(typeof data[keys[i]]!=='string')return false;
   set(elements[i],data[keys[i]]);
  }
  restore();
  const button=findAction('submit');
  if(!button||button.disabled||typeof button.onclick!=='function')return false;
  dismissed=stage;announced=stage;
  button.onclick.call(button);
  return true;
 }catch{return false}
}
const api={submitNative,nativeDismiss(){dismissed=lastStage;announced=lastStage},
 sanitize:isolate,restore,fields:description,fill,
 open(stage='login'){const b=findAction(stage);return !!b&&!b.disabled&&invoke(b)},
 focus(){const e=window.__dfFocused?.isConnected?window.__dfFocused:inputs()[0];if(!e)return false;window.__dfFocused=e;e.focus({preventScroll:true});return document.activeElement===e},
 type(t){const e=window.__dfFocused;if(!e||!e.isConnected)return false;const a=e.selectionStart??e.value.length,b=e.selectionEnd??a;set(e,e.value.slice(0,a)+t+e.value.slice(b));try{e.setSelectionRange(a+t.length,a+t.length)}catch{}return true},
 backspace(){const e=window.__dfFocused;if(!e||!e.isConnected)return false;let a=e.selectionStart??e.value.length,b=e.selectionEnd??a;if(a===b)a=Math.max(0,a-1);set(e,e.value.slice(0,a)+e.value.slice(b));try{e.setSelectionRange(a,a)}catch{}return true}
};
window.__dfLoginFix=api;
if(typeof MutationObserver==='function'){
 const start=()=>{if(!document.body)return;new MutationObserver(rs=>{if(rs.some(r=>r.addedNodes?.length))isolate()}).observe(document.body,{childList:true,subtree:true});isolate()};
 if(document.body)start();else add.call(document,'DOMContentLoaded',start,{once:true});
 // Account UI is rebuilt by the site: inspect DOM changes, not HTML input focus.
 const observe=()=>{if(!document.body)return;new MutationObserver(()=>queueMicrotask(nativeTick)).observe(document.body,{childList:true,subtree:true});nativeTick()};
 if(document.body)observe();else add.call(document,'DOMContentLoaded',observe,{once:true});
}
})();