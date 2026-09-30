import React, {useEffect, useState} from 'react';
import {createRoot} from 'react-dom/client';
import './style.css';
const api = (path, options={}) => fetch(`/api${path}`, {headers:{'X-User-Email':'demo@example.com','Content-Type':'application/json', ...(options.headers||{})}, ...options}).then(r => r.json());
function App(){
 const [stats,setStats]=useState(null), [accounts,setAccounts]=useState([]), [settings,setSettings]=useState({destination_email:''}), [emails,setEmails]=useState([]);
 const load=async()=>{setStats(await api('/stats'));setAccounts(await api('/accounts'));setSettings(await api('/settings'));setEmails(await api('/emails'))}; useEffect(()=>{load()},[]);
 const save=async e=>{e.preventDefault(); await api('/settings',{method:'PUT',body:JSON.stringify(settings)}); load()};
 return <main><h1>Mail Automation</h1><p className="sub">Important Gmail, surfaced and forwarded.</p><section><h2>Connected Gmail accounts</h2>{accounts.length?accounts.map(a=><p key={a.id}>{a.email_address}</p>):<p>No accounts connected. <a href="/api/auth/google">Connect Gmail</a></p>}</section><section><h2>Destination email</h2><form onSubmit={save}><input type="email" value={settings.destination_email||''} placeholder="important@example.com" onChange={e=>setSettings({...settings,destination_email:e.target.value})}/><button>Save</button></form></section><section><h2>Today</h2>{stats&&<div className="stats"><b>{stats.processed_today}<small>Processed</small></b>{Object.entries(stats.categories).map(([k,v])=><b key={k}>{v}<small>{k}</small></b>)}</div>}</section><section><h2>Recent processing activity</h2>{emails.length?emails.map(e=><p key={e.id}><strong>{e.category||'PENDING'}</strong> · {e.sender} — {e.subject}</p>):<p>No processed emails yet.</p>}</section></main> }
createRoot(document.getElementById('root')).render(<App/>);
