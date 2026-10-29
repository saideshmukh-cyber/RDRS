async function getJson(url){const r=await fetch(url);if(!r.ok)throw new Error(await r.text());return r.json()}
function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
async function refresh(){try{const [st,alerts,events,incidents,health]=await Promise.all([getJson('/status'),getJson('/alerts?limit=12'),getJson('/events?limit=12'),getJson('/incidents?limit=12'),getJson('/health')]);
 document.querySelector('#health').textContent=health.status.toUpperCase();document.querySelector('#level').textContent=st.level;document.querySelector('#score').textContent=st.score;document.querySelector('#window').textContent=st.window_events;document.querySelector('#mode').textContent=st.simulation_mode?'SIMULATION':'REVIEW CONFIG';
 document.querySelector('#alerts').innerHTML=alerts.map(a=>`<tr><td>${esc(new Date(a.timestamp).toLocaleTimeString())}</td><td>${esc(a.level)}</td><td>${a.score}</td><td>${esc(a.message)}</td></tr>`).join('')||'<tr><td colspan="4">No alerts</td></tr>';
 document.querySelector('#events').innerHTML=events.map(e=>`<tr><td>${esc(e.event_type)}</td><td title="${esc(e.path)}">${esc(e.path)}</td><td>${e.entropy==null?'—':Number(e.entropy).toFixed(2)}</td><td>${esc(new Date(e.timestamp).toLocaleTimeString())}</td></tr>`).join('')||'<tr><td colspan="4">No events</td></tr>';
 document.querySelector('#incidents').innerHTML=incidents.map(i=>`<tr><td>${i.id}</td><td>${esc(new Date(i.created_at).toLocaleString())}</td><td>${esc(i.level)}</td><td>${i.score}</td><td>${esc(i.signals.join(', '))}</td></tr>`).join('')||'<tr><td colspan="5">No incidents</td></tr>';
 }catch(e){document.querySelector('#health').textContent='API ERROR';console.error(e)}}
refresh();setInterval(refresh,3000);
