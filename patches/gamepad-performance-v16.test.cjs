const fs=require('node:fs'), vm=require('node:vm'), assert=require('node:assert/strict');
const source=fs.readFileSync('app/src/main/assets/gamepad.js','utf8');
let now=0, scans=0, posts=0, events=[];
const frame={contentWindow:{postMessage(){posts++}}};
function Navigator(){}
Object.defineProperty(Navigator.prototype,'getGamepads',{configurable:true,value:()=>[null,null,null,null]});
const navigator=new Navigator();
const window={dispatchEvent:event=>events.push(event)};
const context={
 window,navigator,Navigator,
 performance:{now:()=>now},
 GamepadEvent:class{constructor(){throw new Error('fallback')}},
 Event:class{constructor(type){this.type=type}},
 addEventListener(){},
 document:{querySelectorAll(selector){assert.equal(selector,'iframe');scans++;return [frame]},createElement:()=>({getContext:()=>({})})},
 location:{href:'https://daggerfalljs.dev/'}
};
vm.createContext(context);
vm.runInContext(source,context,{timeout:2000});
const a=navigator.getGamepads(),b=navigator.getGamepads();
assert.equal(a,b,'getGamepads must reuse its result array');
const oldButton=a[0].buttons[0],oldAxes=a[0].axes;
const state={axes:[.5,-.25,0,0],buttons:Array(17).fill(0)};
state.buttons[0]=1;state.buttons[7]=.42;
for(let i=0;i<250;i++)window.__dfUpdate(state);
assert.equal(scans,1,'do not scan iframes on every touch update');
assert.equal(posts,250,'iframe must still receive every delivered state');
assert.equal(events.length,1,'only one connected event');
assert.equal(a[0].buttons[0],oldButton,'button objects must be stable');
assert.equal(a[0].axes,oldAxes,'axes array must be stable');
assert.equal(a[0].buttons[7].value,.42);
assert.equal(a[0].buttons[7].pressed,false);
assert.equal(a[0].buttons[0].pressed,true);
now=600;window.__dfUpdate(state);
assert.equal(scans,2,'rescan after 500ms to pick up new iframes');
window.__dfPad.reset();
assert(a[0].axes.every(x=>x===0));
assert(a[0].buttons.every(x=>x.value===0));
assert.equal(window.__dfPad.status().installed,true);
console.log('PASS v16: no per-frame pad allocation, 17 buttons, 4 axes, iframe cache, event once, reset');
