from pathlib import Path
p=Path('app/src/main/java/dev/daggerfall/mobile/MainActivity.kt')
s=p.read_text()
assert '  var active:EditText=user' in s and '  val keyRows=listOf(' in s
start=s.index('  var active:EditText=user')
end=s.index('  val keyRows=listOf(', start)
replacement='''  var active:EditText=user
  val names=if(confirm==null)listOf("Username","Password") else listOf("Username","Password","Confirm password")
  val selected=TextView(this).apply{
   textSize=15f;setTextColor(Color.rgb(112,224,193));setPadding(12.dp,12.dp,12.dp,8.dp)
  }
  val progress=TextView(this).apply{
   textSize=12f;setTextColor(Color.LTGRAY);setPadding(12.dp,3.dp,12.dp,8.dp)
  }
  val activeColor=Color.rgb(23,81,73)
  val inactiveColor=Color.rgb(26,36,51)
  val entryButtons=mutableListOf<Button>()
  fun updateSelection(){
   val idx=fields.indexOf(active).coerceAtLeast(0)
   selected.text="● Editing: \${names[idx]}  •  \${idx+1} of \${fields.size}"
   progress.text=fields.mapIndexed{ i,e -> "\${names[i]}: \${if(e.length()>0)if(i==0)e.text.toString() else "•".repeat(e.length().coerceAtMost(24)) else "empty"}" }.joinToString("    |    ")
   for((i,e) in fields.withIndex()){
    e.background=surface(if(e===active)activeColor else inactiveColor)
    e.setTextColor(Color.WHITE)
    e.setHintTextColor(if(e===active)Color.WHITE else Color.LTGRAY)
    e.alpha=if(e===active)1f else .75f
    if(i<entryButtons.size){
     entryButtons[i].background=surface(if(e===active)Color.rgb(35,114,99) else inactiveColor)
     entryButtons[i].setTextColor(if(e===active)Color.WHITE else Color.LTGRAY)
    }
   }
  }
  fun pick(e:EditText){active=e;updateSelection()}
  val selector=LinearLayout(this).apply{orientation=LinearLayout.HORIZONTAL}
  for((i,e) in fields.withIndex()){
   val b=Button(this).apply{
    text=names[i];isAllCaps=false;textSize=12f;minWidth=0;minimumWidth=0
    setPadding(3.dp,0,3.dp,0);setOnClickListener{pick(e)}
   }
   entryButtons.add(b)
   selector.addView(b,LinearLayout.LayoutParams(0,48.dp,1f))
   e.setOnClickListener{pick(e)}
   e.addTextChangedListener(object:android.text.TextWatcher{
    override fun beforeTextChanged(t:CharSequence?,st:Int,count:Int,after:Int){}
    override fun onTextChanged(t:CharSequence?,st:Int,before:Int,count:Int){updateSelection()}
    override fun afterTextChanged(t:android.text.Editable?){}
   })
  }
  body.addView(selector)
  body.addView(selected)
  body.addView(progress)
  updateSelection()
'''
s=s[:start]+replacement+s[end:]
s=s.replace('''    "NEXT"->{val index=fields.indexOf(e);pick(fields[(index+1)%fields.size])}''',
'''    "NEXT"->{val index=fields.indexOf(e);pick(fields[(index+1)%fields.size])}''')
# Improve keys: avoid the stock Android material minInset look
s=s.replace('''     textSize=11f;minWidth=0;minimumWidth=0
     setPadding(0,0,0,0)
     setOnClickListener{insertKey(key)}''','''     isAllCaps=false
     textSize=if(key.length==1)16f else 11f
     minWidth=0;minimumWidth=0;minHeight=0;minimumHeight=0
     setPadding(0,0,0,0)
     setTextColor(Color.WHITE)
     background=surface(if(key=="NEXT")Color.rgb(35,114,99) else if(key=="BACK"||key=="SHIFT")Color.rgb(62,75,94) else Color.rgb(35,47,64))
     setOnClickListener{insertKey(key);updateSelection()}''')
s=s.replace('''    keyRow.addView(btn,LinearLayout.LayoutParams(0,42.dp,if(key=="SPACE")2.6f else if(key=="SHIFT"||key=="BACK"||key=="NEXT")1.6f else 1f))''',
'''    keyRow.addView(btn,LinearLayout.LayoutParams(0,46.dp,if(key=="SPACE")2.6f else if(key=="SHIFT"||key=="BACK"||key=="NEXT")1.6f else 1f).apply{setMargins(2.dp,2.dp,2.dp,2.dp)})''')
# Visible status on submit, do not close prematurely; website feedback is asynchronous.
s=s.replace('''  row(body,"Submit" to {''','''  val status=TextView(this).apply{textSize=13f;setTextColor(Color.rgb(112,224,193));text="Ready to sign in";setPadding(12.dp,6.dp,12.dp,8.dp)}
  body.addView(status)
  row(body,"Submit" to {''')
s=s.replace('''    web.evaluateJavascript("window.__dfLoginFix?.submitNative("+JSONObject.quote(values.toString())+")"){r->
     if(r=="true"){user.text.clear();pass.text.clear();confirm?.text?.clear();d.dismiss()}
     else toast("Site form unavailable. Retry from the account page.")
    }''','''    status.text="Submitting to Daggerfall…"
    web.evaluateJavascript("window.__dfLoginFix?.submitNative("+JSONObject.quote(values.toString())+")"){r->
     if(r=="true"){
      status.text="Submitted. Waiting for website response…"
      // Read only the website's public error/note text. Do not log or store credentials.
      fun poll(remaining:Int){
       if(!d.isShowing)return
       web.evaluateJavascript("window.__dfLoginFix?.accountStatus?.()"){raw->
        try{
         val msg=JSONTokener(raw).nextValue() as? String ?: ""
         if(msg.isNotBlank())status.text=msg
         else if(remaining>0)web.postDelayed({poll(remaining-1)},600)
        }catch(_:Exception){if(remaining>0)web.postDelayed({poll(remaining-1)},600)}
       }
      }
      poll(14)
     }else status.text="Form unavailable. Reopen the account screen and retry."
    }''')
assert 'showSoftInputOnFocus=false' in s and 'isFocusable=false' in s
assert 'Editing:' in s and 'status.text="Submitting' in s
p.write_text(s)
print('v12: active-field highlight, readable values, keyboard styling and website response polling')
