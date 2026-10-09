from pathlib import Path
p=Path('app/src/main/java/dev/daggerfall/mobile/MainActivity.kt')
s=p.read_text()
# DaggerfallJS natively parses ?renderscale=0.5 at boot; do not monkeypatch GL or global DPR.
# Rewrite ONLY hardcoded initial navigation to include supported query argument.
import re
matches=list(re.finditer(r'web\.loadUrl\("https://daggerfalljs\.dev/?(?:\?[^"]*)?"\)',s))
assert len(matches)==1, f"Expected one hardcoded initial game load, got {len(matches)}"
s=s[:matches[0].start()] + 'web.loadUrl(gameUrl())' + s[matches[0].end():]
anchor=' fun immersive(){'
assert s.count(anchor)==1
helper=''' // Native DaggerfallJS render scale. No injected rendering patches or modified game files.
 fun gameUrl():String{
  val scale=prefs.getString("render_scale","0.5")?:"0.5"
  val allowed=setOf("1","0.85","0.75","0.67","0.5")
  val selected=if(scale in allowed)scale else "0.5"
  return "https://daggerfalljs.dev/?renderscale="+selected
 }
 fun changeRenderScale(value:String){
  AlertDialog.Builder(this)
   .setTitle("Rendering resolution")
   .setMessage("Apply "+value+" scale? This reloads DaggerfallJS. Save your game first.")
   .setPositiveButton("Reload"){_,_->
    prefs.edit().putString("render_scale",value).apply()
    web.loadUrl(gameUrl())
   }
   .setNegativeButton("Cancel",null).show()
 }
'''
s=s.replace(anchor,helper+anchor,1)
anchor2='  b.addView(label("CONTROLLER PERFORMANCE",12f))'
assert s.count(anchor2)==1
s=s.replace(anchor2,'''  b.addView(label("3D RENDER QUALITY",12f))
  b.addView(label("DaggerfallJS built-in render scale (the world only; HUD stays sharp). 50% is fastest. Save before changing.",13f))
  row(b,"50% Turbo" to {changeRenderScale("0.5")},"67% Fast" to {changeRenderScale("0.67")})
  row(b,"75% Balanced" to {changeRenderScale("0.75")},"85% Quality" to {changeRenderScale("0.85")})
  row(b,"100% Native" to {changeRenderScale("1")})
'''+anchor2,1)
assert 'showAccountEntry(stage:String)' in s
assert 'isFocusable=false;isFocusableInTouchMode=false' in s
p.write_text(s)
print("v19: built-in render scaling, default 50%, selectable 50/67/75/85/100, explicit reload confirmation")
