const $ = id => document.getElementById(id);
function nbTrack(n){ try{ if(window.goatcounter && goatcounter.count) goatcounter.count({path:n, title:n, event:true}); }catch(e){} }
function nbShuffle(a){ a=a.slice(); for(let i=a.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [a[i],a[j]]=[a[j],a[i]]; } return a; }
function nbCap(s){ return s.charAt(0).toUpperCase()+s.slice(1); }
function nbEsc(s){ return String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c])); }
function nbSyll(s){ const m = s.toLowerCase().match(/[aeiouyåäöé]+/g); return m ? m.length : 1; }
function nbItem(n, title, sub){
  return `<li><a href="/namn/${n[5]}/"><b>${title || n[0]}</b><small>${sub || (nbCap(n[2]) + " · " + NB_ORIGIN[n[3]])}</small></a></li>`;
}
function nbSeg(id, opts, state, key, cb){
  const el = $(id);
  el.innerHTML = opts.map(([v,l]) => `<button type="button" data-v="${v}">${l}</button>`).join("");
  const mark = () => el.querySelectorAll("button").forEach(b => b.classList.toggle("on", b.dataset.v === String(state[key])));
  el.querySelectorAll("button").forEach(b => b.onclick = () => { state[key] = b.dataset.v; mark(); if(cb) cb(); });
  mark();
}
const NB_NORDIC = ["Fornnordiskt","Svenskt","Danskt","Isländskt"];
