from pathlib import Path
p=Path('app/src/main/java/dev/daggerfall/mobile/MainActivity.kt')
s=p.read_text()
assert '  val keyRows=listOf(' in s and '  row(body,"Paste" to {' in s
assert '  row(body,"Submit" to {' in s and '   body.addView(keyRow)' in s
s=s.replace('  val keyRows=listOf(', '''  // The keyboard is a separate, permanently visible panel OUTSIDE the scroll view.
  val keyboardHost=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(3.dp,3.dp,3.dp,3.dp);background=surface(Color.rgb(17,25,38))}
  val keyFeedback=TextView(this).apply{
   text="KEYBOARD  •  lowercase";textSize=12f;setTextColor(Color.rgb(112,224,193))
   gravity=Gravity.CENTER_VERTICAL;setPadding(9.dp,5.dp,9.dp,4.dp)
  }
  keyboardHost.addView(keyFeedback,LinearLayout.LayoutParams(-1,25.dp))
  val keyRows=listOf(''',1)
s=s.replace('''   listOf("SHIFT","SPACE","_","-","!","?","BACK","NEXT")''','''   listOf("SHIFT","SYM","SPACE","PASTE","BACK","NEXT")''',1)
s=s.replace('''  var upper=false
  fun insertKey(key:String){''','''  var upper=false
  var symbolMode=false
  val symbolMap=mapOf(
   'q' to '!','w' to '@','e' to '#','r' to '$','t' to '%','y' to '^','u' to '&','i' to '*','o' to '(','p' to ')',
   'a' to '-','s' to '_','d' to '=','f' to '+','g' to '/','h' to ':','j' to ';','k' to '?','l' to '.',
   'z' to '[','x' to ']','c' to '{','v' to '}','b' to '<','n' to '>','m' to '~'
  )
  val letterButtons=mutableListOf<Pair<Button,String>>()
  var shiftButton:Button?=null
  var symbolButton:Button?=null
  fun refreshKeycaps(){
   for((btn,key) in letterButtons)btn.text=if(symbolMode) (symbolMap[key[0]]?.toString()?:key) else if(upper)key.uppercase() else key
   shiftButton?.text=if(upper)"⇧ ON" else "⇧ Shift"
   shiftButton?.background=surface(if(upper)Color.rgb(22,132,110) else Color.rgb(62,75,94))
   symbolButton?.text=if(symbolMode)"ABC" else "123#"
   symbolButton?.background=surface(if(symbolMode)Color.rgb(22,132,110) else Color.rgb(62,75,94))
  }
  fun insertKey(key:String){''',1)
s=s.replace('''    "SHIFT"->upper=!upper''','''    "SHIFT"->{upper=!upper;refreshKeycaps()}''',1)
s=s.replace('''    "NEXT"->{val index=fields.indexOf(e);pick(fields[(index+1)%fields.size])}''','''    "SYM"->{symbolMode=!symbolMode;refreshKeycaps()}
    "PASTE"->{
     val clip=(getSystemService(CLIPBOARD_SERVICE) as android.content.ClipboardManager).primaryClip
     val txt=if(clip!=null&&clip.itemCount>0)clip.getItemAt(0).coerceToText(this).toString() else ""
     if(txt.isNotEmpty())e.text.append(txt)
    }
    "NEXT"->{val index=fields.indexOf(e);pick(fields[(index+1)%fields.size])}''',1)
s=s.replace('''    else->{val value=when(key){"SPACE"->" ";else->if(upper)key.uppercase() else key}''','''    else->{val value=when(key){"SPACE"->" ";else->if(symbolMode&&key.length==1)symbolMap[key[0]]?.toString()?:key else if(upper)key.uppercase() else key}''',1)
s=s.replace('''     setOnClickListener{insertKey(key);updateSelection()}''','''     isFocusable=false;isFocusableInTouchMode=false
     // Native pressed-state tint + haptic feedback, with no input focus.
     val normal=if(key=="NEXT")Color.rgb(23,112,99) else if(key=="BACK"||key=="SHIFT"||key=="SYM")Color.rgb(62,75,94) else Color.rgb(35,47,64)
     background=android.graphics.drawable.StateListDrawable().apply{
      addState(intArrayOf(android.R.attr.state_pressed),surface(Color.rgb(99,181,158)))
      addState(intArrayOf(),surface(normal))
     }
     if(key.length==1&&key[0].isLetter())letterButtons.add(this to key)
     if(key=="SHIFT")shiftButton=this
     if(key=="SYM")symbolButton=this
     setOnClickListener{
      performHapticFeedback(android.view.HapticFeedbackConstants.KEYBOARD_TAP)
      insertKey(key);updateSelection()
      keyFeedback.text=when(key){
       "SHIFT"->if(upper)"SHIFT ON  •  UPPERCASE" else "SHIFT OFF  •  lowercase"
       "SYM"->if(symbolMode)"SYMBOLS  •  tap ABC to return" else "LETTERS  •  tap 123# for symbols"
       "NEXT"->"EDITING  •  "+names[fields.indexOf(active).coerceAtLeast(0)]
       "BACK"->"BACKSPACE  •  character removed"
       else->if(active===pass||active===confirm)"PASSWORD  •  "+active.length()+" characters" else "PRESSED  •  "+(if(key=="SPACE")"Space" else if(symbolMode&&key.length==1)symbolMap[key[0]]?.toString()?:key else if(upper)key.uppercase() else key)
      }
     }''',1)
s=s.replace('''    keyRow.addView(btn,LinearLayout.LayoutParams(0,46.dp,''','''    keyRow.addView(btn,LinearLayout.LayoutParams(0,if(resources.configuration.orientation==android.content.res.Configuration.ORIENTATION_LANDSCAPE)29.dp else if(resources.displayMetrics.heightPixels<750.dp)36.dp else 43.dp,''',1)
s=s.replace('''   body.addView(keyRow)''','''   keyboardHost.addView(keyRow)''',1)
# Paste is a key in the permanently docked keyboard, not a separate scrolling row.
paste_start=s.index('  // Paste using the Android clipboard, without showing the IME.')
paste_end=s.index('  val status=TextView',paste_start)
s=s[:paste_start]+'  refreshKeycaps()\n'+s[paste_end:]
s=s.replace('''  row(body,"Submit" to {''','''  val actionHost=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL}
  row(actionHost,"Submit" to {''',1)
s=s.replace('''  d.show()
  d.window?.setLayout(min(resources.displayMetrics.widthPixels-24.dp,520.dp),min(resources.displayMetrics.heightPixels-48.dp,620.dp))''','''  // Keep keys fixed while the account fields alone may scroll on small screens.
  val scroll=body.parent as ScrollView
  val outer=scroll.parent as LinearLayout
  val landscape=resources.configuration.orientation==android.content.res.Configuration.ORIENTATION_LANDSCAPE
  if(landscape){
   outer.removeView(scroll)
   val columns=LinearLayout(this).apply{orientation=LinearLayout.HORIZONTAL}
   columns.addView(scroll,LinearLayout.LayoutParams(0,-1,0.43f))
   columns.addView(keyboardHost,LinearLayout.LayoutParams(0,-1,0.57f))
   outer.addView(columns,LinearLayout.LayoutParams(-1,0,1f))
  }else{
   outer.addView(keyboardHost,LinearLayout.LayoutParams(-1,-2))
  }
  outer.addView(actionHost,LinearLayout.LayoutParams(-1,-2))
  d.show()
  d.window?.setLayout(
   if(landscape)resources.displayMetrics.widthPixels-20.dp else min(resources.displayMetrics.widthPixels-24.dp,520.dp),
   if(landscape)resources.displayMetrics.heightPixels-20.dp else min(resources.displayMetrics.heightPixels-36.dp,700.dp)
  )''',1)
assert 'keyboardHost.addView(keyRow)' in s
assert 'refreshKeycaps()' in s
assert 'outer.addView(keyboardHost' in s
assert 'row(actionHost,"Submit"' in s
assert '  d.window?.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_HIDDEN' in s
p.write_text(s)
print('v13: fixed keyboard, shift/SYM keycaps, pressed-state feedback, haptics and fixed action row')
