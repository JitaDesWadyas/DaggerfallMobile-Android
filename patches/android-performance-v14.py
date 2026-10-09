from pathlib import Path
p=Path('app/src/main/java/dev/daggerfall/mobile/MainActivity.kt')
s=p.read_text()
start=s.index('  fun send(){if(Uri.parse(web.url?:')
end=s.index('  fun reset(){',start)
new='''  // Batch touch state changes into one IPC call per actual display frame.
  private var inputFrameQueued=false
  private var lastPacket:String?=null
  private val flushInput=android.view.Choreographer.FrameCallback {
   inputFrameQueued=false
   if(Uri.parse(web.url?: "").host=="daggerfalljs.dev"){
    val packet=buildString(320){
     append('{');append('"');append("axes");append('"');append(':');append('[')
     for(i in axes.indices){if(i>0)append(',');append(if(axes[i].isFinite())axes[i] else 0f)}
     append(']');append(',');append('"');append("buttons");append('"');append(':');append('[')
     for(i in buttons.indices){if(i>0)append(',');append(if(buttons[i].isFinite())buttons[i] else 0f)}
     append(']');append('}')
    }
    if(packet!=lastPacket){
     lastPacket=packet
     web.evaluateJavascript("window.__dfUpdate?.("+packet+")",null)
    }
   }
  }
  fun send(){
   if(!inputFrameQueued){
    inputFrameQueued=true
    android.view.Choreographer.getInstance().postFrameCallback(flushInput)
   }
  }
'''
s=s[:start]+new+s[end:]
old='   send();invalidate();return true'
assert s.count(old)==1
s=s.replace(old,'   send();postInvalidateOnAnimation();return true')
needle='  web=WebView(this);root.addView(web,FrameLayout.LayoutParams(-1,-1))'
assert s.count(needle)==1
s=s.replace(needle,needle+'''
  if(Build.VERSION.SDK_INT>=26)web.setRendererPriorityPolicy(WebView.RENDERER_PRIORITY_IMPORTANT,false)
  // Prefer the highest native-resolution display refresh rate (not guaranteed WebGL FPS).
  if(Build.VERSION.SDK_INT>=30){
   val screen=display
   val original=screen?.mode
   val mode=if(screen!=null&&original!=null)screen.supportedModes.filter{
    it.physicalWidth==original.physicalWidth&&it.physicalHeight==original.physicalHeight
   }.maxByOrNull{it.refreshRate} else null
   if(mode!=null){val lp=window.attributes;lp.preferredDisplayModeId=mode.modeId;window.attributes=lp}
  }''')
resume='override fun onResume(){super.onResume();if(::web.isInitialized)web.onResume();immersive()}'
assert s.count(resume)==1
s=s.replace(resume,'override fun onResume(){super.onResume();if(::web.isInitialized)web.onResume();if(::pad.isInitialized)pad.send();immersive()}')
p.write_text(s)
print('Performance v14 applied: per-frame controller IPC, no duplicate state sends, refresh preference')
