import {definitions, monthName, shift, display, change, monthRange, points, csvCell, number} from "./model.mjs";
const byId = id => document.getElementById(id);
const controlIds = ["left","right","month","lag","metric","span"];
const params = new URLSearchParams(location.search);
const cache = new Map();
let edition, revision = 0, downloadRows = [];
function element(tag, value, cls) {
  const item = document.createElement(tag);
  if (value !== undefined) item.textContent = value;
  if (cls) item.className = cls;
  return item;
}
function choose(id, list, value) {
  const select = byId(id);
  if (list) select.replaceChildren(...list.map(([label,v]) => new Option(label,v)));
  const requested = params.get(id);
  select.value = Array.from(select.options).some(o=>o.value===requested) ? requested : value;
}
async function fetchData(path) {
  const response = await fetch("./data/"+path+".json");
  if (!response.ok) throw Error("The saved data could not be read.");
  return response.json();
}
async function records(code) {
  if (!cache.has(code)) cache.set(code, fetchData(code).catch(error=>{cache.delete(code); throw error;}));
  return cache.get(code);
}
function tableHead(labels) {
  const row = element("tr");
  labels.forEach(label=>{const cell=element("th",label); cell.scope="col"; row.append(cell);});
  return row;
}
function metroCard(city, records, month, before) {
  const card = element("article",undefined,"card");
  card.append(element("h3",city.name),element("p",city.province,"sub"));
  const table = element("table");
  table.createTHead().append(tableHead(["Indicator",monthName(month),"Change"]));
  const body=table.createTBody();
  for (const [metric,title] of edition.measures.entries()) {
    const row=body.insertRow(), label=element("th",title);
    label.scope="row"; row.append(label);
    const value=records[month]?.[metric];
    row.insertCell().textContent=display(value,metric);
    row.insertCell().textContent=change(value,records[before]?.[metric],metric);
  }
  card.append(table);
  if(city.smallSample && before < "2025-09") card.append(element("p","Statistics Canada flags greater sampling variability here before September 2025.","note"));
  return card;
}
function plot(months, series, metric) {
  const ns="http://www.w3.org/2000/svg";
  const svg=(tag,attrs,text)=>{
    const n=document.createElementNS(ns,tag);
    for(const [k,v] of Object.entries(attrs)) n.setAttribute(k,v);
    if(text !== undefined) n.textContent=text;
    return n;
  };
  const width=850,height=270, left=70,right=790,top=18,bottom=238;
  const chart=svg("svg",{viewBox:`0 0 ${width} ${height}`,role:"img","aria-label":edition.measures[metric]+" from "+monthName(months[0])+" through "+monthName(months.at(-1))+". Monthly values follow in the table."});
  const all=series.flat().filter(Number.isFinite);
  if(!all.length) return element("p","No published values for this selection.");
  const low=Math.min(...all), high=Math.max(...all);
  const pad=Math.max((high-low)*.12,metric<3?.2:100);
  const min=Math.max(0,low-pad), max=high+pad;
  const y=v=>bottom-(v-min)/(max-min)*(bottom-top);
  const x=i=>months.length === 1 ? (left+right)/2 : left+i/(months.length-1)*(right-left);
  const compact=new Intl.NumberFormat("en-CA",{notation:"compact",maximumFractionDigits:2});
  for(let i=0;i<=4;i++) {
    const v=min+(max-min)*i/4;
    chart.append(svg("line",{x1:left,x2:right,y1:y(v),y2:y(v),stroke:"#d6dfd9"}));
    chart.append(svg("text",{x:left-9,y:y(v)+4,"text-anchor":"end",fill:"#435f64","font-size":15},metric<3?v.toFixed(1)+"%":compact.format(v)));
  }
  chart.append(svg("text",{x:left,y:263,fill:"#435f64","font-size":15},monthName(months[0])));
  if(months.length>1) chart.append(svg("text",{x:right,y:263,fill:"#435f64","text-anchor":"end","font-size":15},monthName(months.at(-1))));
  series.forEach((row,i)=>{
    const colour=i===0?"#116c68":"#a64826";
    chart.append(svg("path",{d:points(row,x,y),fill:"none",stroke:colour,"stroke-width":3,"stroke-dasharray":i?"7 4":"none"}));
    row.forEach((v,t)=>{if(Number.isFinite(v) && !Number.isFinite(row[t-1]) && !Number.isFinite(row[t+1])) chart.append(svg("circle",{cx:x(t),cy:y(v),r:3.5,fill:colour}));});
  });
  return chart;
}
async function render() {
  const version=++revision;
  const values=Object.fromEntries(controlIds.map(id=>[id,byId(id).value]));
  const {left,right,month}=values;
  const metric=Number(values.metric), before=shift(month,-Number(values.lag));
  const months=monthRange(edition.months,month,Number(values.span));
  const pair=[left,right].map(id=>edition.metros.find(m=>m.id===id));
  const link=new URL(location.href);
  link.search=new URLSearchParams(values).toString(); history.replaceState(null,"",link);
  byId("share").href=link.href;
  byId("status").textContent="Loading the comparison…";
  byId("download").disabled=true;
  byId("cards").replaceChildren(); byId("chart").replaceChildren(); byId("legend").replaceChildren(); byId("history").replaceChildren();
  const data=await Promise.all([records(left),records(right)]).catch(()=>null);
  if(version!==revision) return;
  if(!data){ byId("status").textContent="These metro files could not be loaded. Reload the page to try again."; return; }
  byId("cards").replaceChildren(...pair.map((city,i)=>metroCard(city,data[i],month,before)));
  byId("status").textContent=`Period ending ${monthName(month)} · change since ${monthName(before)} · pp = percentage points.`;
  byId("definition").textContent=definitions[metric];
  byId("legend").replaceChildren(...pair.map((c,i)=>{const s=element("span");s.append(element("i",undefined,"key"+(i?" second":"")),c.name);return s;}));
  const series=data.map(rows=>months.map(m=>rows[m]?.[metric]));
  byId("chart").replaceChildren(plot(months,series,metric));
  byId("labels").replaceChildren(tableHead(["Period ending",...pair.map(c=>c.name)]));
  const rows=months.map((m,i)=>{
    const row=element("tr"), label=element("th",monthName(m)); label.scope="row"; row.append(label);
    series.forEach(s=>row.append(element("td",display(s[i],metric))));
    return row;
  });
  byId("history").replaceChildren(...rows.reverse());
  downloadRows=[["end_month","cma","geography","indicator","unit","value","source_status"]];
  months.forEach((m,i)=>pair.forEach((city,c)=>{
    const v=series[c][i];
    downloadRows.push([m,city.id,city.name,edition.measures[metric],metric<3?"percent":"persons",Number.isFinite(v)?v:"",Number.isFinite(v)?"":v||"unavailable"]);
  }));
  byId("download").disabled=false;
}
byId("download").addEventListener("click",()=>{
  const blob=new Blob([downloadRows.map(r=>r.map(csvCell).join(",")).join("\r\n")],{type:"text/csv;charset=utf-8"});
  const url=URL.createObjectURL(blob), link=element("a");
  link.href=url;link.download=`metro-economy-${byId("left").value}-${byId("right").value}-${byId("month").value}.csv`;
  link.click();setTimeout(()=>URL.revokeObjectURL(url),30000);
});
async function start() {
  edition=await fetchData("summary");
  const cities=edition.metros.map(c=>[c.name+" · "+c.province,c.id]);
  choose("left",cities,"205");choose("right",cities,"933");
  choose("month",edition.months.slice().reverse().map(v=>[monthName(v),v]),edition.through);
  choose("metric",edition.measures.map((m,i)=>[m,String(i)]),"0");
  choose("lag",null,"12"); choose("span",null,"60");
  controlIds.forEach(id=>byId(id).addEventListener("change",render));
  await render();
}
start().catch(()=>{byId("status").textContent="The snapshot index could not be loaded. Reload the page or download the complete CSV.";});
