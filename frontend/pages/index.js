import { useState } from 'react'
import axios from 'axios'
import { useRouter } from 'next/router'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const router = useRouter()

  const submit = async (e) => {
    e.preventDefault()
    try {
      const res = await axios.post('/token/', { email: email, password: password })
      const token = res.data.access
      localStorage.setItem('access_token', token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      // redirect to hod dashboard for demo
      router.push('/hod/dashboard')
    } catch (err) {
      setError('Login failed')
    }
  }

  return (
    <div style={{maxWidth:600, margin:'40px auto'}}>
      <h2>Login</h2>
      <form onSubmit={submit}>
        <div>
          <label>Email</label>
          <input value={email} onChange={e=>setEmail(e.target.value)} />
        </div>
        <div style={{marginTop:8}}>
          <label>Password</label>
          <input type="password" value={password} onChange={e=>setPassword(e.target.value)} />
        </div>
        <div style={{marginTop:12}}>
          <button type="submit">Login</button>
        </div>
        {error && <div style={{color:'red'}}>{error}</div>}
      </form>
    </div>
  )
}
