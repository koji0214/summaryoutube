import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [youtubeUrl, setYoutubeUrl] = useState('') // For adding new videos
  const [items, setItems] = useState([])
  const [editingItemId, setEditingItemId] = useState(null) // ID of the item being edited
  const [currentEditUrl, setCurrentEditUrl] = useState('') // URL for the inline edit input

  // YouTube URLから動画IDを抽出するヘルパー関数
  const extractVideoId = (url) => {
    const patterns = [
      /(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)/,
      /(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^?]+)/,
      /(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^?]+)/,
      /(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([^?]+)/
    ];
    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match) {
        return match[1];
      }
    }
    return null;
  };

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

  // 新規アイテム追加フォームの送信処理
  const handleAddSubmit = async (e) => {
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

  // アイテムを削除
  const handleDelete = async (id) => {
    try {
      const response = await fetch(`/api/items/${id}`, {
        method: 'DELETE',
      })
      if (response.ok) {
        fetchItems() // アイテムリストを再取得
      } else {
        console.error("Failed to delete item")
      }
    } catch (error) {
      console.error("Error deleting item:", error)
    }
  }

  // 編集ボタンクリック時の処理
  const handleEditClick = (item) => {
    setEditingItemId(item.id);
    setCurrentEditUrl(item.url); // フォームに現在のURLをセット
  };

  // インライン編集フォームの更新処理
  const handleUpdateSubmit = async (e, itemId) => {
    e.preventDefault();
    try {
      const response = await fetch(`/api/items/${itemId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: currentEditUrl }),
      });
      if (response.ok) {
        setEditingItemId(null); // 編集モードを終了
        setCurrentEditUrl(''); // フォームをクリア
        fetchItems(); // アイテムリストを再取得
      } else {
        console.error("Failed to update item");
      }
    } catch (error) {
      console.error("Error updating item:", error);
    }
  };

  // インライン編集のキャンセル処理
  const handleCancelEdit = () => {
    setEditingItemId(null);
    setCurrentEditUrl('');
  };

  return (
    <>
      <h1>YouTube Video List</h1>

      <h2>Add New Video</h2>
      <form onSubmit={handleAddSubmit}>
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
          {items.map((item) => {
            const videoId = extractVideoId(item.url);
            const isEditing = editingItemId === item.id;

            return (
              <li key={item.id}>
                <strong>Title:</strong> {item.title}<br />
                <strong>Channel:</strong> {item.channel_name}<br />
                {isEditing ? (
                  <form onSubmit={(e) => handleUpdateSubmit(e, item.id)} style={{ display: 'inline' }}>
                    <input
                      type="text"
                      value={currentEditUrl}
                      onChange={(e) => setCurrentEditUrl(e.target.value)}
                      placeholder="Enter new YouTube URL"
                      required
                      style={{ width: '400px' }}
                    />
                    <button type="submit">Update</button>
                    <button type="button" onClick={handleCancelEdit}>Cancel</button>
                  </form>
                ) : (
                  <>
                    <a href={item.url} target="_blank" rel="noopener noreferrer">{item.url}</a><br />
                    <button onClick={() => handleEditClick(item)}>Edit</button>
                    <button onClick={() => handleDelete(item.id)}>Delete</button>
                  </>
                )}
                <br />
                {videoId && (
                  <iframe
                    width="560"
                    height="315"
                    src={`https://www.youtube.com/embed/${videoId}`}
                    frameBorder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                    title={item.title}
                  ></iframe>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </>
  )
}

export default App