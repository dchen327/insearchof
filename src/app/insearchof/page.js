"use client";
import { auth, storage } from "../firebase/config";
import { useEffect, useState } from "react";
import { onAuthStateChanged } from "firebase/auth";
import { useRouter } from "next/navigation";

import { getFirestore, collection, addDoc } from "firebase/firestore";
import { ref as storageRef, uploadBytes, getDownloadURL } from "firebase/storage";
import { v4 as uuidv4 } from "uuid";


export default function Page() {
  const [user, setUser] = useState(null);
  const router = useRouter();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState('');
  const [image, setImage] = useState(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState('');
  const [showTitleTooltip, setShowTitleTooltip] = useState(false);
  const [showDescriptionTooltip, setShowDescriptionTooltip] = useState(false);
  const [showPriceTooltip, setShowPriceTooltip] = useState(false);
  const [showImageTooltip, setShowImageTooltip] = useState(false);


  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      if (currentUser) {
        setUser(currentUser);
      } else {
        router.push("/");
      }
    });

    return () => unsubscribe();
  }, [router]);

  const handleImageChange = (event) => {
    const file = event.target.files[0];
    setImage(file);

    // Set image preview
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreviewUrl(reader.result);
      };
      reader.readAsDataURL(file);
    } else {
      setImagePreviewUrl('');
    }
  };

  const handlePriceChange = (e) => {
    const value = e.target.value;
    const validValue = value.replace(/[^0-9.]/g, '').replace(/(\..*)\./g, '$1');
    const parts = validValue.split('.');
    if (parts.length > 1) {
      parts[1] = parts[1].substring(0, 2);
    }
    const formattedValue = parts.join('.');
    setPrice(formattedValue);
  };

  const uploadRequest = async () => {
    if (!title || price < 0 || !user) {
      alert('Check your inputs or login status.');
      return;
    }

    let imageUrl = '';
    if (image) {
      // Handle image upload first if there is an image
      // Image upload logic goes here, returning an image URL
    }

    const response = await fetch('http://localhost:3000/insearchof/upload', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: title,
        description: description,
        price: parseFloat(price),
        imageUrl: imageUrl
      })
    });

    const data = await response.json();
    if (response.ok) {
      alert('Request uploaded successfully!');
      // Clear form fields here
    } else {
      alert('Failed to upload request: ' + data.message);
    }
  };


  // Define the style for the tooltips outside of the return statement
  const tooltipStyle = {
    position: 'absolute',
    top: '100%',
    left: '0',
    width: '75%', // Tooltip covers 75% of the input field
    backgroundColor: '#f0f0f0',
    padding: '10px',
    borderRadius: '4px',
    boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
    zIndex: '10',
    marginTop: '5px'
  };



  return (
    <>
      <div style={{
        textAlign: 'center',
        margin: '20px 0',
      }}>
        <h1>ISO Requester</h1>
      </div>

      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
        maxWidth: '500px',
        margin: '0px auto',
        padding: '20px',
        boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
        borderRadius: '8px',
        backgroundColor: '#fff',
      }}>
        {['title', 'description', 'price', 'image'].map((field) => (
          <div key={field} style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: '5px' }}>
            {field === 'title' && <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Title (Required)"
              style={{ padding: '10px', fontSize: '16px', border: '1px solid #ccc', borderRadius: '4px', flexGrow: 1 }}
            />}
            {field === 'description' && <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Description (Optional)"
              style={{ height: '100px', padding: '10px', fontSize: '16px', border: '1px solid #ccc', borderRadius: '4px', flexGrow: 1, resize: 'none' }}
            />}
            {field === 'price' && <>
              <label style={{ marginRight: '5px', fontSize: '16px' }}>$</label>
              <input
                type="text"
                value={price}
                onChange={handlePriceChange}
                placeholder="Price (Optional)"
                style={{ padding: '10px', fontSize: '16px', border: '1px solid #ccc', borderRadius: '4px', flexGrow: 1 }}
              />
            </>}
            {field === 'image' && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <label style={{ flexGrow: 1, display: 'flex', alignItems: 'center' }}>
                  <span style={{ marginRight: '10px', fontSize: '16px' }}>Image (optional)</span>
                  <input
                    type="file"
                    onChange={handleImageChange}
                    accept="image/*"
                    style={{ padding: '10px', fontSize: '16px', border: '1px solid #ccc', borderRadius: '4px', flexGrow: 1 }}
                  />
                </label>
              </div>
            )}
            <button
              onClick={() => {
                // Close any open tooltip and open the clicked one
                setShowTitleTooltip(field === 'title' ? !showTitleTooltip : false);
                setShowDescriptionTooltip(field === 'description' ? !showDescriptionTooltip : false);
                setShowPriceTooltip(field === 'price' ? !showPriceTooltip : false);
                setShowImageTooltip(field === 'image' ? !showImageTooltip : false);
              }}
              style={{ position: 'relative', zIndex: '20' }}
            >
              ?
            </button>
            {showTitleTooltip && field === 'title' && <div style={tooltipStyle}>
              The title of item or service requested
            </div>}
            {showDescriptionTooltip && field === 'description' && <div style={tooltipStyle}>
              The description of item or service requested
            </div>}
            {showPriceTooltip && field === 'price' && <div style={tooltipStyle}>
              The price you are willing to pay for such item or service. Leaving it empty also means 0 dollars
            </div>}
            {showImageTooltip && field === 'image' && <div style={tooltipStyle}>
              The image of item or service you are requesting
            </div>}
          </div>
        ))}

        {imagePreviewUrl && <img src={imagePreviewUrl} alt="Preview" style={{ maxWidth: '100%', marginTop: '20px' }} />}
      </div>

      <div className="buttons" style={{
        maxWidth: '500px',
        margin: '20px auto',
        display: 'flex',
        justifyContent: 'center'
      }}>
        <button className="button is-light" onClick={uploadRequest} style={{
          padding: '10px 20px',
          fontSize: '16px',
          backgroundColor: '#007BFF',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}>
          Upload Request
        </button>
      </div>
    </>
  );

}