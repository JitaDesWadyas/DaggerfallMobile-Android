from pathlib import Path
p=Path('app/src/main/java/dev/daggerfall/mobile/MainActivity.kt')
s=p.read_text()
s=s.replace('pad=PadView();root.addView(pad,FrameLayout.LayoutParams(-1,-1))','pad=PadView();root.addView(pad,FrameLayout.LayoutParams(-1,-1));pad.visibility=View.GONE')
s=s.replace('row(b,"Native sign in" to {d.dismiss();nativeLogin()},"Android keyboard" to {d.dismiss();keyboard()})','row(b,"Android keyboard" to {d.dismiss();keyboard()})')
start=s.find(' fun nativeLogin(){')
end=s.find(' fun hideCustomKeyboard(){',start)
if start<0 or end<0:raise SystemExit('Native login methods not found')
s=s[:start]+s[end:]
s=s.replace('pad.controlsEnabled=!pad.controlsEnabled;pad.invalidate()','pad.controlsEnabled=!pad.controlsEnabled;syncPadVisibility();pad.invalidate()')
s=s.replace('pad.edit=!pad.edit;pad.invalidate()','pad.edit=!pad.edit;syncPadVisibility();pad.invalidate()')
s=s.replace('private var keyboardPanel:LinearLayout?=null','private var keyboardPanel:LinearLayout?=null\n fun syncPadVisibility(){if(::pad.isInitialized)pad.visibility=if(pad.controlsEnabled||pad.edit)View.VISIBLE else View.GONE}')
s=s.replace('pad.visibility=if(insets.isVisible(WindowInsets.Type.ime()))View.GONE else View.VISIBLE','pad.visibility=if(insets.isVisible(WindowInsets.Type.ime()))View.GONE else if(pad.controlsEnabled||pad.edit)View.VISIBLE else View.GONE')
s=s.replace('web.postDelayed({web.requestFocus();(getSystemService(INPUT_METHOD_SERVICE) as InputMethodManager).showSoftInput(web,InputMethodManager.SHOW_IMPLICIT)},80)','web.postDelayed({web.requestFocus();web.evaluateJavascript("document.activeElement?.focus?.()",null);(getSystemService(INPUT_METHOD_SERVICE) as InputMethodManager).showSoftInput(web,InputMethodManager.SHOW_IMPLICIT)},120)')
s=s.replace('fun keyboard(){hideCustomKeyboard();pad.reset();web.evaluateJavascript("window.__dfLoginFix?.focus()") { web.post {window.decorView.systemUiVisibility=View.SYSTEM_UI_FLAG_LAYOUT_STABLE;web.requestFocus();if(Build.VERSION.SDK_INT>=30)window.insetsController?.show(WindowInsets.Type.ime());(getSystemService(INPUT_METHOD_SERVICE) as InputMethodManager).showSoftInput(web,InputMethodManager.SHOW_IMPLICIT)} }}','fun keyboard(){hideCustomKeyboard();pad.reset();web.requestFocus();web.evaluateJavascript("window.__dfLoginFix?.focus()"){web.postDelayed({window.decorView.systemUiVisibility=View.SYSTEM_UI_FLAG_LAYOUT_STABLE;web.requestFocus();(getSystemService(INPUT_METHOD_SERVICE) as InputMethodManager).showSoftInput(web,InputMethodManager.SHOW_IMPLICIT);if(Build.VERSION.SDK_INT>=30)window.insetsController?.show(WindowInsets.Type.ime())},120)}}')
s=s.replace('override fun onConfigurationChanged(config:android.content.res.Configuration){','override fun onConfigurationChanged(config:android.content.res.Configuration){')
assert 'fun nativeLogin()' not in s and '"Native sign in"' not in s
assert 'syncPadVisibility()' in s
p.write_text(s)
print('Applied Android input, overlay and menu patch')
