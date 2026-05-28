import useSWR from 'swr'
import axios from 'axios'
import { useEffect } from 'react'

export default function HODDashboard(){
  useEffect(()=>{
    const token = localStorage.getItem('access_token')
    if(token) axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
  },[])

  const { data, error } = useSWR('/hod/dashboard/')

  if(error) return <div>Error loading dashboard</div>
  if(!data) return <div>Loading...</div>

  return (
    <div style={{padding:24}}>
      <h2>{data.page_title}</h2>
      <div style={{display:'flex',gap:12,marginTop:12}}>
        <div style={{flex:1,padding:12,background:'#f8f9fa',borderRadius:8}}>
          <h3>{data.total_students}</h3>
          <div>Students in Scope</div>
        </div>
        <div style={{flex:1,padding:12,background:'#f8f9fa',borderRadius:8}}>
          <h3>{data.total_subject}</h3>
          <div>Subjects in Scope</div>
        </div>
        <div style={{flex:1,padding:12,background:'#f8f9fa',borderRadius:8}}>
          <h3>{data.total_staff}</h3>
          <div>Faculty in Scope</div>
        </div>
        <div style={{flex:1,padding:12,background:'#f8f9fa',borderRadius:8}}>
          <h3>{data.total_leave}</h3>
          <div>Your Leave Requests</div>
        </div>
      </div>

      <div style={{display:'flex',gap:16,marginTop:18}}>
        <div style={{flex:2}}>
          <h4>Holidays</h4>
          <table style={{width:'100%',borderCollapse:'collapse'}}>
            <thead>
              <tr>
                <th style={{border:'1px solid #ddd',padding:8}}>#</th>
                <th style={{border:'1px solid #ddd',padding:8}}>Name</th>
                <th style={{border:'1px solid #ddd',padding:8}}>From</th>
                <th style={{border:'1px solid #ddd',padding:8}}>To</th>
              </tr>
            </thead>
            <tbody>
              {data.holiday_rows.map((row,idx)=> (
                <tr key={idx}>
                  <td style={{border:'1px solid #ddd',padding:8}}>{idx+1}</td>
                  <td style={{border:'1px solid #ddd',padding:8}}>{row.name}</td>
                  <td style={{border:'1px solid #ddd',padding:8}}>{row.from}</td>
                  <td style={{border:'1px solid #ddd',padding:8}}>{row.to}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div style={{flex:1}}>
          <h4>Announcement</h4>
          <div style={{padding:12,background:'#fff',border:'1px solid #eee'}}>{data.announcement || 'No announcements'}</div>

          <h4 style={{marginTop:16}}>Class Routine</h4>
          <div style={{padding:12,background:'#fff',border:'1px solid #eee'}}>
            {data.class_routine.map((r, i)=> (
              <div key={i} style={{display:'flex',justifyContent:'space-between',padding:'6px 0'}}>
                <div><strong>{r[0]}</strong></div>
                <div style={{color:'#666'}}>{r[1]}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
