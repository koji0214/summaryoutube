import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const [items, setItems] = useState([])

  // アイテムリストを取得
  const fetchItems = () => {
    fetch('/api/items/')
      .then((res) => res.json())
      .then((data) => setItems(data))
      .catch((err) => console.error("Error fetching items:", err))
  }

  useEffect(() => {
    fetchItems()
  }, [])

  // アイテムを送信
  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch('/api/items/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: youtubeUrl }),
      })
      if (response.ok) {
        setYoutubeUrl('') // フォームをクリア
        fetchItems() // アイテムリストを再取得
      } else {
        console.error("Failed to add item")
      }
    } catch (error) {
      console.error("Error adding item:", error)
    }
  }

  return (
    <>
      <h1>YouTube Video List</h1>

      <h2>Add New Video</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={youtubeUrl}
          onChange={(e) => setYoutubeUrl(e.target.value)}
          placeholder="Enter YouTube URL"
          required
        />
        <button type="submit">Add Video</button>
      </form>

      <h2>Videos from Database</h2>
      {items.length === 0 ? (
        <p>No videos yet.</p>
      ) : (
        <ul>
          {items.map((item) => (
            <li key={item.id}>
              <strong>Title:</strong> {item.title}<br />
              <strong>Channel:</strong> {item.channel_name}<br />
              <a href={item.url} target="_blank" rel="noopener noreferrer">{item.url}</a>
            </li>
          ))}
        </ul>
      )}
    </>
  )
}

export default App