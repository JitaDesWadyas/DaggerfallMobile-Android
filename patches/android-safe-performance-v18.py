from pathlib import Path
p=Path('app/src/main/java/dev/daggerfall/mobile/MainActivity.kt')
s=p.read_text()
old='''  fun send(){if(Uri.parse(web.url?:"").host!="daggerfalljs.dev")return;web.evaluateJavascript("window.__dfUpdate?.({axes:[${axes.joinToString()}],buttons:[${buttons.joinToString()}]})",null)}'''
assert s.count(old)==1,'Refuse patch: v15 controller source unexpected'
new='''  // Optimize only Android touch transport. Leave gamepad JS untouched.
  private var pendingInputFrame=false
  private var previousInputState:String?=null
  private val emitInputFrame=Runnable {
   pendingInputFrame=false
   emitInputNow(true)
  }
  private fun emitInputNow(skipDuplicate:Boolean){
   if(Uri.parse(web.url?:"").host!="daggerfalljs.dev"){
    previousInputState=null
    return
   }
   val packet="window.__dfUpdate?.({axes:[${axes.joinToString()}],buttons:[${buttons.joinToString()}]})"
   if(skipDuplicate&&packet==previousInputState)return
   previousInputState=packet
   web.evaluateJavascript(packet,null)
  }
  fun send(){
   if(!prefs.getBoolean("optimized_input_enabled",true)){
    if(pendingInputFrame){removeCallbacks(emitInputFrame);pendingInputFrame=false}
    emitInputNow(false)
    return
   }
   if(!pendingInputFrame){
    pendingInputFrame=true
    postOnAnimation(emitInputFrame)
   }
  }'''
s=s.replace(old,new,1)
old='''   send();invalidate();return true'''
assert s.count(old)==1,'Refuse patch: touch update location changed'
s=s.replace(old,'''   send();postInvalidateOnAnimation();return true''',1)
needle='''  b.addView(label("APP MENU BUTTON",12f))'''
assert s.count(needle)==1,'Refuse patch: menu anchor changed'
s=s.replace(needle,'''  b.addView(label("CONTROLLER PERFORMANCE",12f))
  b.addView(label("Optimized input batches touch events. Turn it off if controls behave strangely.",13f))
  row(b,"Optimized ON" to {prefs.edit().putBoolean("optimized_input_enabled",true).apply();toast("Optimized controller enabled")},"Original mode" to {prefs.edit().putBoolean("optimized_input_enabled",false).apply();toast("Original controller restored")})
'''+needle,1)
for check in ['showAccountEntry(stage:String)','isFocusable=false;isFocusableInTouchMode=false','fun applyMenuButtonPosition()']:
 assert check in s,check
p.write_text(s)
print('v18: Android-only input batching, opt-out, original JS shim preserved')
