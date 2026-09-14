import test from "node:test";
import assert from "node:assert/strict";
import { safePath, sameOriginMutation, publicOrigin } from "../src/lib/proxy-policy.mjs";
test("proxy only accepts literal API path segments", () => {
  assert.equal(safePath(["patient", "today"]), true);
  for (const p of [[".."], ["%2e%2e"], ["https:"], ["auth/me"], []])
    assert.equal(safePath(p), false);
});
test("cookie-authenticated mutations require the same origin", () => {
  assert.equal(
    sameOriginMutation("POST", "https://attacker.test", "https://movena.test"),
    false,
  );
  assert.equal(sameOriginMutation("POST", null, "https://movena.test"), false);
  assert.equal(sameOriginMutation("POST", null, null), false);
  assert.equal(
    sameOriginMutation("POST", "https://movena.test", "https://movena.test"),
    true,
  );
  assert.equal(sameOriginMutation("GET", null, "https://movena.test"), true);
});
test('public origin comes from canonical deployment config and invalid configuration fails closed',()=>{
  const origin=publicOrigin('https://movena.example','http://localhost:3100');
  assert.equal(sameOriginMutation('POST','https://movena.example',origin),true);
  assert.equal(sameOriginMutation('POST','https://attacker.example',origin),false);
  assert.equal(publicOrigin(undefined,'http://127.0.0.1:3100'),'http://127.0.0.1:3100');
  for(const value of ['', 'https://user:secret@movena.example','https://movena.example/path','javascript:alert(1)','https://movena.example?query=1']) {
    assert.equal(publicOrigin(value,'http://localhost:3100'),null);
    assert.equal(sameOriginMutation('POST',null,publicOrigin(value,'http://localhost:3100')),false);
  }
});
