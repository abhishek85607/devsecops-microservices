import React, { useState, useEffect } from 'react'

export default function App() {
  const [data, setData] = useState([])
  const [source, setSource] = useState('')
  const [message, setMessage] = useState('')

  const fetchData = async () => {
    try {
      const res = await fetch('/api/v1/data')
      const json = await res.json()
      setData(json.data || [])
      setSource(json.source || 'N/A')
    } catch (err) {
      console.error(err)
    }
  }

  const submitData = async (e) => {
    e.preventDefault()
    if (!message) return
    await fetch('/api/v1/data', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    })
    setMessage('')
    fetchData()
  }

  useEffect(() => {
    fetchData()
  }, [])

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', padding: '30px' }}>
      <h2>DevSecOps 4-Tier Microservices Dashboard</h2>
      <p>Data Source State: <strong>{source}</strong></p>
      
      <form onSubmit={submitData}>
        <input 
          type="text" 
          value={message} 
          onChange={(e) => setMessage(e.target.value)} 
          placeholder="Enter audit log payload" 
          style={{ padding: '8px', width: '250px' }}
        />
        <button type="submit" style={{ padding: '8px 16px', marginLeft: '10px' }}>Commit Log</button>
      </form>

      <ul style={{ marginTop: '20px' }}>
        {Array.isArray(data) && data.map((item, idx) => (
          <li key={idx}>{item.message} - <small>{item.created_at}</small></li>
        ))}
      </ul>
    </div>
  )
}
