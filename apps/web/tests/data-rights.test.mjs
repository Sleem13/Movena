import test from "node:test";
import assert from "node:assert/strict";
import {
  newDataRightsKey,
  validDataRightsDetails,
} from "../src/lib/data-rights.mjs";

test("data rights details enforce the contract limit", () => {
  assert.equal(validDataRightsDetails("x".repeat(2000)), true);
  assert.equal(validDataRightsDetails("x".repeat(2001)), false);
});

test("retry keys are non-empty and rotate", () => {
  const first = newDataRightsKey();
  assert.ok(first.length > 8);
  assert.notEqual(first, newDataRightsKey());
});
