(()=>{
 if(window.__dfPad)return;
 const nativeGetPads=navigator.getGamepads?.bind(navigator);
 let reads=0,connected=false,installed=false,error='';
 const pad={
  id:'Xbox 360 Controller (Daggerfall Mobile)',index:0,connected:true,mapping:'standard',
  timestamp:performance.now(),axes:[0,0,0,0],
  buttons:Array.from({length:17},()=>({pressed:false,touched:false,value:0})),vibrationActuator:null
 };
 const slots=[pad,null,null,null];
 const descriptor=Object.getOwnPropertyDescriptor(Navigator.prototype,'getGamepads');
 const getPads=()=>{
  reads++;
  // Reuse result array without losing other connected physical gamepads.
  if(nativeGetPads){try{const real=nativeGetPads();for(let i=1;i<4;i++)slots[i]=real?.[i]??null}catch{}}
  return slots;
 };
 try{Object.defineProperty(navigator,'getGamepads',{value:getPads,configurable:true});installed=navigator.getGamepads===getPads}
 catch(e){error=String(e);if(!descriptor||descriptor.configurable){try{Object.defineProperty(Navigator.prototype,'getGamepads',{value:getPads,configurable:true});installed=navigator.getGamepads===getPads}catch(e2){error=String(e2)}}}
 const buttons=pad.buttons,axes=pad.axes;
 function update(s){
  let active=false;
  for(let i=0;i<4;i++){const v=s.axes[i]||0;axes[i]=v;if(v!==0)active=true}
  for(let i=0;i<17;i++){
   const v=s.buttons[i]||0,b=buttons[i];b.value=v;b.pressed=v>0.5;b.touched=v>0;
   if(v>0)active=true;
  }
  pad.timestamp=performance.now();
  if(!connected&&active){
   connected=true;let event;
   try{event=new GamepadEvent('gamepadconnected',{gamepad:pad})}
   catch{event=new Event('gamepadconnected');Object.defineProperty(event,'gamepad',{value:pad})}
   window.dispatchEvent(event);
  }
 }
 window.__dfPad={
  update,
  status(){return {installed,error,reads,axes:pad.axes,buttons:buttons.map(b=>b.value),frame:location.href,webgl2:!!document.createElement('canvas').getContext('webgl2')}},
  reset(){update({axes:[0,0,0,0],buttons:Array(17).fill(0)})}
 };
 addEventListener('message',e=>{if(e.origin==='https://daggerfalljs.dev'&&e.data?.dfMobileState)update(e.data.dfMobileState)});
 let frames=[],nextScan=-1;
 window.__dfUpdate=s=>{
  update(s);
  const now=performance.now();
  if(now>=nextScan){
   frames=Array.from(document.querySelectorAll('iframe'),f=>f.contentWindow).filter(Boolean);
   nextScan=now+(frames.length?1000:250);
  }
  for(const frame of frames)try{frame.postMessage({dfMobileState:s},'https://daggerfalljs.dev')}catch{}
 };
})();