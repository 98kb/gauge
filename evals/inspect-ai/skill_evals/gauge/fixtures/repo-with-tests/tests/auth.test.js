import { test } from "node:test";
import assert from "node:assert";
import { isExpired } from "../src/auth/tokens.js";

test("fresh token is not expired", () =>
  assert.equal(isExpired({ issuedAt: Date.now() }), false));
