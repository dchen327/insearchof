"use client";
import { auth } from "../firebase/config";
import { useEffect, useState } from "react";
import { onAuthStateChanged } from "firebase/auth";
import { useRouter } from "next/navigation";


export default function Page() {
  const [user, setUser] = useState(null);
  const router = useRouter();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState('');
  const [image, setImage] = useState(null); 

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      if (currentUser) {
        setUser(currentUser);
      } else {
        router.push("/");
      }
    });

    // Cleanup subscription on unmount
    return () => unsubscribe();
  }, [router]);

  const handleImageChange = (event) => {
    setImage(event.target.files[0]);  // Set the image file
  };

  const uploadRequest = async () => {
    if (!title) {
      alert('Title is required.');
      return;
    }
    
    if (price < 0) {
      alert('Price cannot be negative.');
      return;
    }
      
    if (!user) {
      alert('You need to be logged in to submit a request.');
      return;
    }

    const token = await user.getIdToken();  // Firebase ID token

    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    formData.append('price', price === '' ? '0' : price);
    if (image) {
      formData.append('image', image);  // image file to the FormData object
    }

    const config = {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'  
      }
    };

    try {
      // attempt upload (i have no code right now)
      alert('Request uploaded successfully: ' + title + ' ' + description + ' ' + price);
    } catch (error) {
      console.error('Error uploading request:', error);
      alert('Failed to upload request: ' + (error.response?.data?.detail || 'Unknown error') + ': ' + title + ' ' + description + ' ' + price);
    }
  };


  return (
    <>
      <div>
        <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Title" />
        <textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Description" />
        <input type="number" value={price} onChange={(e) => setPrice(parseFloat(e.target.value))} placeholder="Price" />
        <input type="file" onChange={handleImageChange} accept="image/png, image/jpeg, image/jpg, image/gif, image/svg, image/webp" />
      </div>
      <div className="buttons">
        <button className="button is-light" onClick={uploadRequest}>
          Upload Request
        </button>
      </div>
    </>
  );
}
