import test from 'node:test';
import assert from 'node:assert/strict';
import {notePayload,uncertainNote} from '../src/lib/visit-notes.mjs';
test('visit notes default to private and preserve text as text',()=>{
  const form=new FormData();form.set('summary',' <b>Synthetic text</b>\nSecond line ');form.set('recommendations','  ');
  assert.deepEqual(notePayload(form),{summary:'<b>Synthetic text</b>\nSecond line',recommendations:null,patient_visible:false});
  form.set('patient_visible','on');assert.equal(notePayload(form).patient_visible,true);
});
test('uncertain write outcomes require an identical retry, validation errors remain editable',()=>{
  for(const status of [0,409,500,502,503,504])assert.equal(uncertainNote(status),true);
  for(const status of [400,401,403,404,422])assert.equal(uncertainNote(status),false);
});
