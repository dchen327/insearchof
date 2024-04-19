"use client";
import { auth, storage } from "../firebase/config";
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

    // prevent any non-numeric characters from being entered
    // allow only one decimal point
    const validValue = value.replace(/[^0-9.]/g, '').replace(/(\..*)\./g, '$1');
    const parts = validValue.split('.');

    // allow only two decimal places max
    if (parts.length > 1) {
      parts[1] = parts[1].substring(0, 2);
    }
    const formattedValue = parts.join('.');
    setPrice(formattedValue);
  };

  const uploadRequest = async () => {
    // Validate input fields
    if (!title) {
      alert('Title is required.');
      return;
    }

    // If price is empty, set it to 0
    const finalPrice = price === '' ? 0 : parseFloat(price);
    if (finalPrice < 0) {
      alert('Price cannot be negative.');
      return;
    }

    // Check if the user is logged in
    if (!user) {
      alert('You need to be logged in to submit a request.');
      return;
    }

    // Upload the image first, if it exists
    try {
      let imageUrl = '';
      try {
        if (image) {
          const formData = new FormData();
          formData.append('file', image);

          // Include the user_id in the URL
          const imageResponse = await fetch(`/api/insearchof/upload-image/${user.uid}`, {
            method: 'POST',
            body: formData, // Send the file as FormData
          });

          if (!imageResponse.ok) {
            throw new Error('Image upload failed');
          }

          const imageData = await imageResponse.json();
          imageUrl = imageData.image_url; // Get the image URL from the backend
        }
      } catch (error) {
        // error handling for image upload
        console.error('Failed to fetch:', error);
        // If the error object has a response with JSON, log that as well
        if (error.response) {
          error.response.json().then((json) => {
            console.log('Error details:', json);
          });
        }
        alert('An error occurred. Please check the console for more details.');
        return;
      }

      // Prepare request data
      const requestData = {
        title: title,
        description: description,
        price: parseFloat(finalPrice),
        image_url: imageUrl,
        type: 'request',
        trans_comp: false,
        user_id: user.uid
      };

      // Send the request data to the backend
      const response = await fetch('api/insearchof/upload', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      });

      const data = await response.json();
      if (response.ok) {
        alert('Request uploaded successfully!');
        // Clear the form
        setTitle('');
        setDescription('');
        setPrice('');
        setImage(null);
        setImagePreviewUrl('');
      } else {
        alert('Failed to upload request: ' + data.message);
      }
    } catch (error) {
      console.error('Failed to fetch:', error);
      alert('An error occurred. Please try again.');
    }
  };


  const updateRequest = async () => {
    // todo
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
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                <label style={{ flexGrow: 1, display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  <span style={{ marginBottom: '10px', fontSize: '16px' }}>Image (optional)</span>
                  <input
                    type="file"
                    onChange={handleImageChange}
                    accept="image/*"
                    style={{
                      padding: '10px',
                      fontSize: '16px',
                      border: '1px solid #ccc',
                      borderRadius: '4px',
                      width: '100%'  // Ensure the input takes the full width of its parent container
                    }}
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
        <button className="button is-light" onClick={updateRequest} style={{
          padding: '10px 20px',
          fontSize: '16px',
          backgroundColor: '#007BFF',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}>
          Update Request
        </button>

      </div>
    </>
  );

}