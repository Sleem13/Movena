import test from 'node:test';
import assert from 'node:assert/strict';
import {historyPath, historyRepetitions, historyStatusKey} from '../src/lib/history.mjs';
test('older history requests retain explicit outcome filtering and reject invalid pages',()=>{
  const query = new URLSearchParams(historyPath(40,'rejected').split('?')[1]);
  assert.equal(query.get('offset'),'40'); assert.equal(query.get('limit'),'20'); assert.equal(query.get('status'),'rejected');
  for(const offset of [-1,NaN,1.5]) assert.throws(()=>historyPath(offset,''),RangeError);
  assert.throws(()=>historyPath(0,'unknown'),RangeError);
});
test('history preserves real zero and never presents rejected or unknown counts as success',()=>{
  assert.equal(historyRepetitions({status:'success',total_reps:0}),0);
  for(const status of ['rejected','error','unrecognized']) assert.equal(historyRepetitions({status,total_reps:9}),null);
  for(const total_reps of [null,undefined,NaN,Infinity,-1,0.5,'10']) assert.equal(historyRepetitions({status:'success',total_reps}),null);
  assert.equal(historyStatusKey('old-pending-state'),'historyUnknown');
  assert.equal(historyStatusKey('constructor'),'historyUnknown');
});
