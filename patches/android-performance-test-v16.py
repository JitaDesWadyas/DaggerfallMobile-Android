from pathlib import Path
p=Path('app/src/main/java/dev/daggerfall/mobile/MainActivity.kt')
s=p.read_text()
needle='''  b.addView(label("DISPLAY AND CONTROLLER",12f))'''
assert s.count(needle)==1, "Known v15 menu not found"
s=s.replace(needle,needle+'''
  row(b,"Test fluidity" to {d.dismiss();measureWebViewFrames()})''')
needle=''' fun slider(parent:LinearLayout,label:String,max:Int,value:Int,change:(Int)->Unit){'''
assert s.count(needle)==1, "Known v15 utility boundary not found"
block=''' // A temporary WebView rAF probe, OFF except during the 2.2s test.
 // Reports the renderer's animation callback rate, not the game's actual GPU FPS.
 fun measureWebViewFrames(){
  if(isDestroyed)return
  toast("Measuring WebView animation frames…")
  val js="""(function(){
   var start=performance.now(),frames=0;
   window.__dfPerfSample={done:false,frames:0,elapsed:0};
   function tick(now){
    frames++;
    if(now-start<2200){requestAnimationFrame(tick)}
    else{window.__dfPerfSample={done:true,frames:frames,elapsed:now-start}}
   }
   requestAnimationFrame(tick)
  })()"""
  web.evaluateJavascript(js,null)
  web.postDelayed({
   if(isDestroyed)return@postDelayed
   web.evaluateJavascript("JSON.stringify(window.__dfPerfSample||{})"){ raw->
    try{
     val decoded=org.json.JSONTokener(raw).nextValue() as? String ?: "{}"
     val data=JSONObject(decoded)
     val elapsed=data.optDouble("elapsed",0.0)
     val frames=data.optInt("frames",0)
     val fps=if(elapsed>0)(frames*1000.0/elapsed).roundToInt() else 0
     val webViewVersion=WebView.getCurrentWebViewPackage()?.versionName ?: "unknown"
     val body="WebView rAF: "+(if(elapsed>0)"$fps frames/sec" else "not available")+
      "\\nFrames: $frames over "+elapsed.roundToInt()+" ms"+
      "\\nWebView: $webViewVersion"+
      "\\n\\nThis measures animation callbacks, not actual game GPU FPS. Compare the same location against Chrome."
     AlertDialog.Builder(this).setTitle("Daggerfall performance").setMessage(body).setPositiveButton("OK",null).show()
    }catch(_:Exception){toast("Measurement unavailable")}
   }
  },2600L)
 }
'''
s=s.replace(needle,block+needle)
assert "isFocusable=false;isFocusableInTouchMode=false" in s
p.write_text(s)
print("v16: optional 2.2s rAF probe, zero persistent frame observers")
