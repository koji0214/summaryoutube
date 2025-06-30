import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)
  const [message, setMessage] = useState('')
  const [itemName, setItemName] = useState('')
  const [items, setItems] = useState([])

  // バックエンドからのメッセージを取得
  useEffect(() => {
    fetch('/api/')
      .then((res) => res.json())
      .then((data) => setMessage(data.Hello))
      .catch((err) => console.error("Error fetching root message:", err))
  }, [])

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
        body: JSON.stringify({ name: itemName }),
      })
      if (response.ok) {
        setItemName('') // フォームをクリア
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
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.jsx</code> and save to test HMR
        </p>
        <p>Message from backend: {message}</p>
      </div>

      <h2>Add New Item</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={itemName}
          onChange={(e) => setItemName(e.target.value)}
          placeholder="Enter item name"
          required
        />
        <button type="submit">Add Item</button>
      </form>

      <h2>Items from Database</h2>
      {items.length === 0 ? (
        <p>No items yet.</p>
      ) : (
        <ul>
          {items.map((item) => (
            <li key={item.id}>{item.name}</li>
          ))}
        </ul>
      )}

      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  )
}

export default App