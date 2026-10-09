from pathlib import Path
p=Path('app/src/main/java/dev/daggerfall/mobile/MainActivity.kt')
s=p.read_text()
old='''  fun send(){if(Uri.parse(web.url?:"").host!="daggerfalljs.dev")return;web.evaluateJavascript("window.__dfUpdate?.({axes:[${axes.joinToString()}],buttons:[${buttons.joinToString()}]})",null)}'''
assert s.count(old)==1,"Expected stable v13 PadView.send(), refusing to modify unknown source"
new='''  // Deliver at most one controller update per display frame and never send
  // the same state twice. No extra WebView renderer or WebGL API hooks.
  private val lastAxes=FloatArray(4)
  private val lastButtons=FloatArray(17)
  private var hasLastState=false
  private var frameQueued=false
  private val deliverFrame=android.view.Choreographer.FrameCallback {
   frameQueued=false
   if(!isDestroyed&&Uri.parse(web.url?:"").host=="daggerfalljs.dev"){
    if(!hasLastState||!axes.contentEquals(lastAxes)||!buttons.contentEquals(lastButtons)){
     axes.copyInto(lastAxes);buttons.copyInto(lastButtons);hasLastState=true
     web.evaluateJavascript("window.__dfUpdate?.({axes:[${axes.joinToString()}],buttons:[${buttons.joinToString()}]})",null)
    }
   }else hasLastState=false
  }
  fun send(){
   if(!frameQueued){
    frameQueued=true
    android.view.Choreographer.getInstance().postFrameCallback(deliverFrame)
   }
  }'''
s=s.replace(old,new)
old='''   send();invalidate();return true'''
assert s.count(old)==1, "Expected PadView onTouchEvent end"
s=s.replace(old,'''   send();postInvalidateOnAnimation();return true''',1)
# Keep the login focus workaround, all native input widgets and their overlays untouched.
assert 'showAccountEntry(stage:String)' in s
assert 'isFocusable=false;isFocusableInTouchMode=false' in s
assert 'keyboardHost.addView(keyRow)' in s
p.write_text(s)
print('v16 Kotlin: coalesced controller IPC, duplicate state suppression, frame-timed redraw')
