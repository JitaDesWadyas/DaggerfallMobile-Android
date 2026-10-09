const test=require('node:test'),assert=require('node:assert/strict'),fs=require('fs'),vm=require('vm');
const src=fs.readFileSync('app/src/main/assets/login-fix.js','utf8');
test('isolation removes HTML attrs and preserves account state handler',()=>{
 assert.match(src,/for\(const a of Array\.from\(e\.attributes\)\)if\(!harmless\.has/);
 assert.match(src,/saved\.set\(e,\{attrs,oninput/);
 assert.match(src,/e\.oninput=s\.oninput/);
});
test('restoration happens BEFORE site submit and avoids synthetic click',()=>{
 assert.match(src,/if\(submit\)\{\s*restore\(\)/);
 assert.match(src,/if\(typeof b\.onclick==='function'\)\{b\.onclick\.call\(b\);return true\}/);
});
test('valid JavaScript',()=>{new vm.Script(src)});
