export const definitions = [
  "Unemployed people as a percentage of the labour force (people who are employed or unemployed).",
  "Employed people as a percentage of the survey population aged 15 and older.",
  "People in the labour force as a percentage of the survey population aged 15 and older.",
  "Estimated number of employed people in the metropolitan area.",
  "Estimated number of people classified as unemployed under the Labour Force Survey definition.",
  "Estimated number of employed and unemployed people combined.",
  "Estimated survey population aged 15 and older."
];
export const number = new Intl.NumberFormat("en-CA");
export function monthName(key) {
  return new Intl.DateTimeFormat("en-CA", {month:"short",year:"numeric",timeZone:"UTC"}).format(new Date(key+"-15T00:00:00Z"));
}
export function shift(month, offset) {
  const [year, part] = month.split("-").map(Number);
  return new Date(Date.UTC(year, part-1+offset, 1)).toISOString().slice(0,7);
}
export function display(value, metric) {
  if (!Number.isFinite(value)) return value === "x" ? "Suppressed" : "Unavailable";
  return metric < 3 ? value.toFixed(1)+"%" : number.format(value);
}
export function change(current, base, metric) {
  if (![current,base].every(Number.isFinite)) return "Unavailable";
  const delta = Math.round((current-base)*10)/10;
  return (delta>0 ? "+" : "")+(metric<3 ? delta.toFixed(1)+" pp" : number.format(delta));
}
export function monthRange(months, end, span) {
  const valid = months.filter(m => m <= end);
  return span > 0 ? valid.slice(-span) : valid;
}
export function points(points, x, y) {
  let next = "M";
  return points.map((p,i) => {
    if (!Number.isFinite(p)) { next = "M"; return ""; }
    const entry = next+x(i).toFixed(2)+" "+y(p).toFixed(2);
    next = "L";
    return entry;
  }).join(" ");
}
export function csvCell(v) { return '"'+String(v??"").replaceAll('"','""')+'"'; }
