from pathlib import Path
p=Path('app/src/main/java/dev/daggerfall/mobile/MainActivity.kt')
s=p.read_text()
assert 'showSoftInputOnFocus=false' in s
s=s.replace('showSoftInputOnFocus=false','showSoftInputOnFocus=false\n   isFocusable=false;isFocusableInTouchMode=false\n   isCursorVisible=false')
start=s.index('  var active:EditText=user')
end=s.index('  val keyRows=listOf(',start)
s=s[:start]+'''  var active:EditText=user
  // Never give focus to either account field; tapping only changes target.
  // No WebView input focus, no native EditText focus, no Android IME.
  fun pick(e:EditText){active=e}
  for(e in fields)e.setOnClickListener{pick(e)}
  row(body,"Username" to {pick(user)},"Password" to {pick(pass)})
  if(confirm!=null)row(body,"Confirm password" to {pick(confirm)})
'''+s[end:]
s=s.replace('  user.requestFocus()\n','')
s=s.replace('fields[(index+1)%fields.size].requestFocus()','pick(fields[(index+1)%fields.size])')
assert 'user.requestFocus()' not in s
assert 'isFocusable=false' in s
assert 'pick(fields[(index+1)%fields.size])' in s
p.write_text(s)
print('Account entry: zero input focus, next changes active target only')
