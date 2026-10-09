from pathlib import Path
import os,re
main=Path('app/src/main/AndroidManifest.xml')
s=main.read_text()
assert 'android:label="Daggerfall Mobile"' in s
s=s.replace('android:label="Daggerfall Mobile"','android:label="Daggerfall Mobile" android:icon="@drawable/ic_launcher"',1)
main.write_text(s)
icon=Path('app/src/main/res/drawable/ic_launcher.xml')
icon.parent.mkdir(parents=True,exist_ok=True)
icon.write_bytes(Path('app-icon/ic_launcher.xml').read_bytes())
gradle=Path('app/build.gradle')
s=gradle.read_text()
build_num=int(os.environ.get('GITHUB_RUN_NUMBER','1'))
version_code=10000+build_num
assert re.search(r'\bversionCode\s+\d+\b',s)
s=re.sub(r'\bversionCode\s+\d+\b','versionCode '+str(version_code),s,count=1)
s=re.sub(r"\bversionName\s+'[^']+'", "versionName '1.15."+str(build_num)+"'",s,count=1)
gradle.write_text(s)
print('v15: restored v13 startup path, launcher icon, versionCode',version_code)
