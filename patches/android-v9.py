from pathlib import Path
p=Path('app/src/main/java/dev/daggerfall/mobile/MainActivity.kt')
s=p.read_text()
s=s.replace('window.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE)','window.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_NOTHING)')
s=s.replace('root.setPadding(0,0,0,ime.bottom);','')
s=s.replace('pad=PadView();root.addView(pad,FrameLayout.LayoutParams(-1,-1))','pad=PadView();root.addView(pad,FrameLayout.LayoutParams(-1,-1));pad.visibility=View.GONE')
s=s.replace('pad.visibility=if(insets.isVisible(WindowInsets.Type.ime()))View.GONE else View.VISIBLE','pad.visibility=if(insets.isVisible(WindowInsets.Type.ime()))View.GONE else if(pad.controlsEnabled||pad.edit)View.VISIBLE else View.GONE')
s=s.replace('pad.controlsEnabled=!pad.controlsEnabled;pad.invalidate()','pad.controlsEnabled=!pad.controlsEnabled;pad.visibility=if(pad.controlsEnabled||pad.edit)View.VISIBLE else View.GONE;pad.invalidate()')
s=s.replace('pad.edit=!pad.edit;pad.invalidate()','pad.edit=!pad.edit;pad.visibility=if(pad.controlsEnabled||pad.edit)View.VISIBLE else View.GONE;pad.invalidate()')
s=s.replace('row(b,"Native sign in" to {d.dismiss();nativeLogin()},"Android keyboard" to {d.dismiss();keyboard()})','row(b,"Android keyboard" to {d.dismiss();keyboard()})')
start=s.index(' fun nativeLogin(){')
end=s.index(' fun hideCustomKeyboard(){',start)
s=s[:start]+s[end:]
old='  if(WebViewFeature.isFeatureSupported(WebViewFeature.WEB_MESSAGE_LISTENER)) WebViewCompat.addWebMessageListener(web,"dfInputFocus",setOf("https://daggerfalljs.dev")){_,_,origin,main,_ ->if(origin.host=="daggerfalljs.dev"&&main)web.postDelayed({web.requestFocus();(getSystemService(INPUT_METHOD_SERVICE) as InputMethodManager).showSoftInput(web,InputMethodManager.SHOW_IMPLICIT)},80)}'
bridge='''  if(WebViewFeature.isFeatureSupported(WebViewFeature.WEB_MESSAGE_LISTENER)) WebViewCompat.addWebMessageListener(web,"dfAccountEntry",setOf("https://daggerfalljs.dev")){_,message,origin,main,_ ->
   if(origin.host=="daggerfalljs.dev"&&main){val stage=message.data?:"";web.post{if(stage=="login"||stage=="register")showAccountEntry(stage)}}
  }'''
assert old in s
s=s.replace(old,bridge)
new='''
 private var accountEntryDialog:Dialog?=null
 private var currentEntryStage:String?=null
 fun showAccountEntry(stage:String){
  if(isFinishing||accountEntryDialog?.isShowing==true||currentEntryStage==stage)return
  currentEntryStage=stage
  pad.reset()
  val(d,body)=panelDialog(if(stage=="register")"Create Daggerfall account" else "Sign in to Daggerfall")
  accountEntryDialog=d
  body.addView(label("Use the Android keyboard here. The game's HTML fields do not receive focus.",13f))
  fun field(h:String,secret:Boolean):EditText=EditText(this).apply{
   hint=h;isSingleLine=true
   inputType=if(secret)android.text.InputType.TYPE_CLASS_TEXT or android.text.InputType.TYPE_TEXT_VARIATION_PASSWORD else android.text.InputType.TYPE_CLASS_TEXT or android.text.InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS
   setTextColor(Color.WHITE);setHintTextColor(Color.LTGRAY)
   setPadding(12.dp,12.dp,12.dp,12.dp);background=surface(Color.rgb(26,36,51))
  }
  val user=field("Username",false);val pass=field("Password",true)
  body.addView(label("Username",13f));body.addView(user,LinearLayout.LayoutParams(-1,52.dp))
  body.addView(label("Password",13f));body.addView(pass,LinearLayout.LayoutParams(-1,52.dp))
  val confirm=if(stage=="register")field("Confirm password",true) else null
  if(confirm!=null){body.addView(label("Confirm password",13f));body.addView(confirm,LinearLayout.LayoutParams(-1,52.dp))}
  row(body,"Submit" to {
   val u=user.text.toString();val pw=pass.text.toString()
   if(u.isBlank()||pw.isBlank())toast("Enter username and password")
   else if(confirm!=null&&pw!=confirm.text.toString())toast("Passwords do not match")
   else {
    val values=JSONObject().put("handle",u).put("password",pw)
    if(confirm!=null)values.put("confirm",confirm.text.toString())
    web.evaluateJavascript("window.__dfLoginFix?.submitNative("+JSONObject.quote(values.toString())+")"){r->
     if(r=="true"){user.text.clear();pass.text.clear();confirm?.text?.clear();d.dismiss()}
     else toast("Site form unavailable. Retry from the account page.")
    }
   }
  },"Cancel" to {d.dismiss()})
  d.setOnDismissListener {accountEntryDialog=null;currentEntryStage=null;web.evaluateJavascript("window.__dfLoginFix?.nativeDismiss()",null)}
  d.show()
  d.window?.setLayout(min(resources.displayMetrics.widthPixels-24.dp,520.dp),min(resources.displayMetrics.heightPixels-48.dp,620.dp))
  d.window?.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE)
 }
'''
s=s.replace(' fun hideCustomKeyboard(){',new+'\n fun hideCustomKeyboard(){')
s=s.replace('fun keyboard(){hideCustomKeyboard();pad.reset();web.evaluateJavascript("window.__dfLoginFix?.focus()") { web.post {window.decorView.systemUiVisibility=View.SYSTEM_UI_FLAG_LAYOUT_STABLE;web.requestFocus();if(Build.VERSION.SDK_INT>=30)window.insetsController?.show(WindowInsets.Type.ime());(getSystemService(INPUT_METHOD_SERVICE) as InputMethodManager).showSoftInput(web,InputMethodManager.SHOW_IMPLICIT)} }}','fun keyboard(){hideCustomKeyboard();pad.reset();web.evaluateJavascript("window.__dfLoginFix?.focus()",null)}')
assert 'fun nativeLogin()' not in s and 'showAccountEntry(stage:String)' in s
p.write_text(s)
print('Applied native account entry v9')
