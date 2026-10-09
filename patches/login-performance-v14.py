from pathlib import Path
p=Path('app/src/main/assets/login-fix.js')
s=p.read_text()
start=s.index("if(typeof MutationObserver==='function'){")
# Keep login state machine, submitNative, accountStatus and the working focus-free flow.
old=s[start:]
assert "const observe=()=>{if(!document.body)return;new MutationObserver(()=>queueMicrotask(nativeTick))" in old
new="""if(typeof MutationObserver==='function'){
 let accountRoot=null;
 function accountChanged(records){
  for(const record of records){
   if(accountRoot?.contains(record.target))return true;
   for(const nodes of [record.addedNodes,record.removedNodes]){
    for(const node of nodes){
     if(node.nodeType!==1)continue;
     if(node.matches?.('.px-acctwin')||node.querySelector?.('.px-acctwin'))return true;
    }
   }
  }
  return false;
 }
 const start=()=>{
  if(!document.body)return;
  let queued=false;
  const refresh=()=>{
   queued=false;
   accountRoot=document.querySelector('.px-acctwin');
   if(accountRoot)isolate();
   nativeTick();
  };
  new MutationObserver(records=>{
   if(queued||!accountChanged(records))return;
   queued=true;
   queueMicrotask(refresh);
  }).observe(document.body,{childList:true,subtree:true});
  refresh();
 };
 if(document.body)start();else add.call(document,'DOMContentLoaded',start,{once:true});
}
})();"""
s=s[:start]+new
assert s.count('new MutationObserver(')==1
assert 'submitNative(json)' in s and 'accountStatus' in s
p.write_text(s)
print('Performance v14: single account-only MutationObserver; login callbacks unchanged')
