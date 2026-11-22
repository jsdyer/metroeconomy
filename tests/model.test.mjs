import test from "node:test";
import assert from "node:assert/strict";
import {shift,change,display,monthRange,points,csvCell} from "../web/model.mjs";
test("year boundaries, rates, missing values and counts",()=>{
  assert.equal(shift("2026-01",-1),"2025-12");
  assert.equal(change(5.4,5.8,0),"-0.4 pp");
  assert.equal(change(303200,293200,3),"+10,000");
  assert.equal(change(0,null,2),"Unavailable");
  assert.equal(display("x",4),"Suppressed");
  assert.equal(display(0,4),"0");
});
test("history ends at selected month, shows discontinuities and allows CSV quotation",()=>{
  assert.deepEqual(monthRange(["2026-01","2026-02","2026-03"],"2026-02",1),["2026-02"]);
  assert.equal(points([4,null,3],i=>i,v=>v),"M0.00 4.00  M2.00 3.00");
  assert.equal(csvCell('a"b'),'"a""b"');
});
