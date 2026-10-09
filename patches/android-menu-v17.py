from pathlib import Path
p=Path('app/src/main/java/dev/daggerfall/mobile/MainActivity.kt')
s=p.read_text()
old='''  root.addView(menuButton,FrameLayout.LayoutParams(58.dp,48.dp,Gravity.TOP or Gravity.RIGHT))'''
assert s.count(old)==1
s=s.replace(old,'''  root.addView(menuButton,FrameLayout.LayoutParams(58.dp,48.dp,Gravity.TOP or Gravity.RIGHT))
  applyMenuButtonPosition()''',1)
boundary=''' fun immersive(){'''
assert s.count(boundary)==1
methods=''' // Menu button preferences are native UI only; no change to WebView or game inputs.
 fun applyMenuButtonPosition(){
  if(!::menuButton.isInitialized)return
  val position=prefs.getInt("menu_button_position",0).coerceIn(0,4)
  val hidden=position==4
  menuButton.visibility=if(hidden)View.GONE else View.VISIBLE
  val gravity=when(position){
   1->Gravity.TOP or Gravity.LEFT
   2->Gravity.BOTTOM or Gravity.RIGHT
   3->Gravity.BOTTOM or Gravity.LEFT
   else->Gravity.TOP or Gravity.RIGHT
  }
  val params=FrameLayout.LayoutParams(58.dp,48.dp,gravity)
  val margin=10.dp
  params.setMargins(margin,margin,margin,margin)
  menuButton.layoutParams=params
 }
 fun setMenuButtonPosition(position:Int){
  prefs.edit().putInt("menu_button_position",position).apply()
  applyMenuButtonPosition()
  if(position==4)toast("Menu hidden: press Android Back to open settings")
 }
'''
s=s.replace(boundary,methods+boundary,1)
needle='''  b.addView(label("BROWSER",12f))'''
assert s.count(needle)==1
s=s.replace(needle,'''  b.addView(label("APP MENU BUTTON",12f))
  b.addView(label("Position of the ☰ button. Android Back always opens this menu.",13f))
  row(b,"Top right" to {setMenuButtonPosition(0)},"Top left" to {setMenuButtonPosition(1)})
  row(b,"Bottom right" to {setMenuButtonPosition(2)},"Bottom left" to {setMenuButtonPosition(3)})
  row(b,"Hide ☰" to {setMenuButtonPosition(4)},"Show ☰" to {setMenuButtonPosition(0)})
'''+needle,1)
# Back handling already calls settings; preserve the path, but give native account dialog a chance to close itself.
assert 'override fun onBackPressed()' in s
assert 'settings()}' in s
assert 'showAccountEntry(stage:String)' in s
p.write_text(s)
print('v17: native menu position/hide preferences + Android Back remains as menu shortcut')
