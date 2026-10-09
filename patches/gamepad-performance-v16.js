(()=>{
 if(window.__dfPad)return;
 const original=navigator.getGamepads?.bind(navigator);
 let reads=0,connected=false,installed=false,error='';
 const pad={id:'Xbox 360 Controller (Daggerfall Mobile)',index:0,connected:true,mapping:'standard',timestamp:performance.now(),axes:[0,0,0,0],buttons:Array.from({length:17},()=>({pressed:false,touched:false,value:0})),vibrationActuator:null};
 const desc=Object.getOwnPropertyDescriptor(Navigator.prototype,'getGamepads');
 // The game polls every animation frame. Keep the returned list and button
 // objects stable instead of allocating arrays/objects on each read.
 const gamepads=[pad,null,null,null];
 const getter=()=>{
  reads++;
  if(original){
   try{
    const native=original();
    for(let i=1;i<4;i++)gamepads[i]=native?.[i]??null;
   }catch{}
  }
  return gamepads;
 };
 try{Object.defineProperty(navigator,'getGamepads',{value:getter,configurable:true});installed=navigator.getGamepads===getter;}
 catch(e){error=String(e);if(!desc||desc.configurable){try{Object.defineProperty(Navigator.prototype,'getGamepads',{value:getter,configurable:true});installed=navigator.getGamepads===getter;}catch(e2){error=String(e2)}}}
 function update(state){
  const axes=state.axes||[],buttons=state.buttons||[];
  let active=false;
  for(let i=0;i<4;i++){
   const v=Number(axes[i])||0;
   pad.axes[i]=v;
   if(v!==0)active=true;
  }
  for(let i=0;i<17;i++){
   const v=Number(buttons[i])||0,b=pad.buttons[i];
   b.value=v;b.pressed=v>0.5;b.touched=v>0;
   if(v>0)active=true;
  }
  pad.timestamp=performance.now();
  if(!connected&&active){
   connected=true;
   let event;
   try{event=new GamepadEvent('gamepadconnected',{gamepad:pad})}
   catch{event=new Event('gamepadconnected');Object.defineProperty(event,'gamepad',{value:pad})}
   window.dispatchEvent(event);
  }
 }
 window.__dfPad={
  update,
  status(){return {installed,error,reads,axes:pad.axes,buttons:pad.buttons.map(b=>b.value),frame:location.href,webgl2:!!document.createElement('canvas').getContext('webgl2')}},
  reset(){update({axes:[0,0,0,0],buttons:Array(17).fill(0)})}
 };
 addEventListener('message',e=>{if(e.origin==='https://daggerfalljs.dev'&&e.data?.dfMobileState)update(e.data.dfMobileState)});
 let frames=null,scanAt=0;
 window.__dfUpdate=state=>{
  update(state);
  const now=performance.now();
  if(now>=scanAt){
   frames=document.querySelectorAll('iframe');
   scanAt=now+500;
  }
  if(frames)for(const f of frames)try{f.contentWindow?.postMessage({dfMobileState:state},'https://daggerfalljs.dev')}catch{}
 };
})();
