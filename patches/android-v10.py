from pathlib import Path
p=Path('app/src/main/java/dev/daggerfall/mobile/MainActivity.kt')
s=p.read_text()
needle='''  body.addView(label("Use the Android keyboard here. The game's HTML fields do not receive focus.",13f))'''
assert needle in s, 'v9 dialog intro not found'
s=s.replace(needle,'''  body.addView(label("Offline keyboard: Android system keyboard stays closed.",13f))''')
needle='''   setTextColor(Color.WHITE);setHintTextColor(Color.LTGRAY)'''
assert needle in s
s=s.replace(needle,'''   showSoftInputOnFocus=false
   setTextColor(Color.WHITE);setHintTextColor(Color.LTGRAY)''')
needle='''  row(body,"Submit" to {'''
assert needle in s
board='''  // These are real Android fields but never request the Android IME.
  // Key presses only edit the native EditText, never the game's WebView.
  val fields=mutableListOf(user,pass)
  if(confirm!=null)fields.add(confirm)
  var active:EditText=user
  for(e in fields)e.setOnFocusChangeListener {_,hasFocus->if(hasFocus)active=e}
  user.requestFocus()
  val keyRows=listOf(
   listOf("1","2","3","4","5","6","7","8","9","0"),
   listOf("q","w","e","r","t","y","u","i","o","p"),
   listOf("a","s","d","f","g","h","j","k","l"),
   listOf("z","x","c","v","b","n","m",".","@"),
   listOf("SHIFT","SPACE","_","-","!","?","BACK","NEXT")
  )
  var upper=false
  fun insertKey(key:String){
   val e=active
   val a=e.selectionStart.coerceAtLeast(0)
   val b=e.selectionEnd.coerceAtLeast(a)
   val text=e.text
   when(key){
    "SHIFT"->upper=!upper
    "NEXT"->{val index=fields.indexOf(e);fields[(index+1)%fields.size].requestFocus()}
    "BACK"->{if(a!=b)text.delete(a,b) else if(a>0)text.delete(a-1,a)}
    else->{val value=when(key){"SPACE"->" ";else->if(upper)key.uppercase() else key}
      text.replace(a,b,value)
    }
   }
  }
  for(keys in keyRows){
   val keyRow=LinearLayout(this).apply{orientation=LinearLayout.HORIZONTAL}
   for(key in keys){
    val btn=Button(this).apply{
     text=when(key){"SPACE"->"Space";"BACK"->"⌫";"NEXT"->"Next";else->key}
     textSize=11f;minWidth=0;minimumWidth=0
     setPadding(0,0,0,0)
     setOnClickListener{insertKey(key)}
    }
    keyRow.addView(btn,LinearLayout.LayoutParams(0,42.dp,if(key=="SPACE")2.6f else if(key=="SHIFT"||key=="BACK"||key=="NEXT")1.6f else 1f))
   }
   body.addView(keyRow)
  }
  // Paste using the Android clipboard, without showing the IME.
  row(body,"Paste" to {
   val clip=(getSystemService(CLIPBOARD_SERVICE) as android.content.ClipboardManager).primaryClip
   val txt=if(clip!=null&&clip.itemCount>0)clip.getItemAt(0).coerceToText(this).toString() else ""
   if(txt.isNotEmpty()){
    val a=active.selectionStart.coerceAtLeast(0)
    val b=active.selectionEnd.coerceAtLeast(a)
    active.text.replace(a,b,txt)
   }
  })
'''
s=s.replace(needle,board+needle)
s=s.replace('''  d.window?.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE)''','''  d.window?.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_HIDDEN or WindowManager.LayoutParams.SOFT_INPUT_ADJUST_NOTHING)
  (getSystemService(INPUT_METHOD_SERVICE) as InputMethodManager).hideSoftInputFromWindow(user.windowToken,0)''')
assert 'showSoftInputOnFocus=false' in s
assert 'keyRows=listOf' in s
assert 'SOFT_INPUT_STATE_ALWAYS_HIDDEN' in s
p.write_text(s)
print('v10: embedded keypad active; Android IME disabled for account fields')
