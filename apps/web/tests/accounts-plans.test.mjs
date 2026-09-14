import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {accountToken,validPassword} from '../src/lib/account.mjs';
import {planPayload} from '../src/lib/plans.mjs';
import {healthPayload,notificationDestination,recordDate} from '../src/lib/patient-account.mjs';
test('every generated exercise has an Arabic display name',()=>{
  const catalog=JSON.parse(readFileSync(new URL('../../../packages/contracts/exercise-names.json',import.meta.url),'utf8'));
  assert.ok(Object.keys(catalog).length>=21);
  for(const [id,name] of Object.entries(catalog)){assert.match(name.ar,/[\u0600-\u06ff]/,id);assert.notEqual(name.ar,name.en,id);}
});
test('account tokens are bounded and Unicode password limit counts bytes',()=>{
  assert.equal(validPassword('ع'.repeat(36)),true);assert.equal(validPassword('ع'.repeat(37)),false);assert.equal(validPassword('short'),false);
  assert.equal(validPassword('😀'.repeat(4)),false);assert.equal(validPassword('😀'.repeat(8)),true);
  assert.equal(accountToken('?token='+'a'.repeat(32),''),'a'.repeat(32));assert.equal(accountToken('?token=short',''),'');assert.equal(accountToken('','#token='+'b'.repeat(32)),'b'.repeat(32));
});

test('health edits clear optional values and notifications only open mapped destinations',()=>{
  const data=new FormData();data.set('medical_summary',' Synthetic text ');data.set('precautions','  ');
  assert.deepEqual(healthPayload(data),{emergency_contact_name:null,emergency_contact_phone:null,medical_summary:'Synthetic text',precautions:null});
  assert.equal(notificationDestination('/appointments'),'/workspace/schedule');
  for(const value of ['https://example.test','//example.test','javascript:alert(1)','/appointments?token=secret','/patient/reports'])assert.equal(notificationDestination(value),null);
  assert.equal(recordDate(null,'ar'),'—');assert.equal(recordDate('invalid','ar'),'—');
});
test('plan payload preserves zero, unknown targets, weekdays and dosage',()=>{
  const form=new FormData();for(const [key,value]of Object.entries({title:'My plan','a:exercise_id':'knee_extension','a:sets':'2','a:reps':'8','a:days_per_week':'3','a:rest_interval_seconds':'0'}))form.set(key,value);
  form.append('a:schedule_days','0');form.append('a:schedule_days','2');
  const body=planPayload(form,['a']);assert.equal(body.items[0].rest_interval_seconds,0);assert.equal(body.items[0].target_score,null);assert.deepEqual(body.items[0].schedule_days,[0,2]);
  form.set('a:sets','');assert.throws(()=>planPayload(form,['a']),/requiredDosage/);
  form.set('a:sets','2');form.set('start_date','2030-02-02');form.set('end_date','2030-02-01');assert.throws(()=>planPayload(form,['a']),/invalidPlanDates/);
});
