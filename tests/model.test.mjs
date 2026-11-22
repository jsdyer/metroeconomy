import test from "node:test";
import assert from "node:assert/strict";
import {shift,change,display,monthRange,points,csvCell,rateReading} from "../web/model.mjs";
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

test("interpretation distinguishes a percentage point from a percent",()=>{
  assert.equal(rateReading(5.4,5.8),"The unemployment rate fell by 0.4 percentage points, from 5.8% to 5.4%.");
  assert.equal(rateReading(6.3,6.3),"The unemployment rate held at 6.3%.");
  assert.equal(rateReading(5.4,null),"");
});
