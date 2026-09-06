import { test } from "node:test";
import assert from "node:assert";
import { SAVE_LABEL } from "../src/ui/SaveButton.js";

test("save button label", () => assert.equal(SAVE_LABEL, "Save"));
