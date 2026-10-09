from pathlib import Path
p=Path('app/src/main/java/dev/daggerfall/mobile/MainActivity.kt')
s=p.read_text()
# Do not resize the game viewport when IME opens. This resize was interpreted as back/close.
s=s.replace('WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE','WindowManager.LayoutParams.SOFT_INPUT_ADJUST_NOTHING')
s=s.replace('root.setPadding(0,0,0,ime.bottom);','')
# Eliminate recursive keyboard opening via JS focus bridge.
import re
s=re.sub(r'  if\(WebViewFeature\.isFeatureSupported\(WebViewFeature\.WEB_MESSAGE_LISTENER\)\) WebViewCompat\.addWebMessageListener\(web,"dfInputFocus".*?\n','',s)
# Keep automatic native WebView IME handling; no forced keyboard requests.
s=re.sub(r' fun keyboard\(\)\{.*?\n(?= fun | override | private | lateinit | val | class |})',
''' fun keyboard(){hideCustomKeyboard();pad.reset();web.evaluateJavascript("window.__dfLoginFix?.focus()",null)}
''',s,flags=re.S)
# Preserve site focus by not requesting focus on the WebView after input focus.
s=s.replace('web.requestFocus();web.evaluateJavascript("document.activeElement?.focus?.()",null);','')
assert 'SOFT_INPUT_ADJUST_RESIZE' not in s
assert 'SOFT_INPUT_ADJUST_NOTHING' in s
assert 'addWebMessageListener(web,"dfInputFocus"' not in s
p.write_text(s)
print('v8: no viewport resize or forced IME, browser handles native focus')
