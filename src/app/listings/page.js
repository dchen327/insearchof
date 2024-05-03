// listings/page.js
"use client";
import { auth, storage } from "../firebase/config";
import { useEffect, useState } from "react";
import { onAuthStateChanged } from "firebase/auth";
import { useRouter } from "next/navigation";
import Image from 'next/image';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

export default function ListingsPage() {
  const [user, setUser] = useState(null);
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [image, setImage] = useState(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState("");
  const [category, setCategory] = useState("All");
  const [isRenting, setIsRenting] = useState(false);
  const [activeTab, setActiveTab] = useState("upload");
  const [listings, setListings] = useState([]);
  const [selectedListingId, setSelectedListingId] = useState("");
  // const [availabilityDates, setAvailabilityDates] = useState("");
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(new Date());


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

  const validateFormAndUser = (title, price, user) => {
    if (!title) {
      alert("Title is required.");
      return null;
    }
    const finalPrice = price === '' ? 0 : parseFloat(price);
    if (isNaN(finalPrice) || finalPrice < 0) {
      alert("Price must be a valid number and cannot be negative.");
      return null;
    }
    if (!user) {
      alert("You need to be logged in to list an item.");
      return null;
    }
    return finalPrice;
  };

  const resetForm = () => {
    setTitle("");
    setDescription("");
    setPrice("");
    setImage(null);
    setImagePreviewUrl("");
    setIsRenting(false);
    setCategory("All");
    // setAvailabilityDates("");
    setStartDate("");
    setEndDate("");
  };

  const uploadListing = async () => {
    const finalPrice = validateFormAndUser(title, price, user);
    if (finalPrice === null) {
      return;
    }

    let imageUrl = "";
    try {
      imageUrl = await uploadImage(image);
    } catch (error) {
      console.error("Failed to fetch:", error);
      if (error.response) {
        error.response.json().then((json) => {
          console.log("Error details:", json);
        });
      }
      alert("An error occurred. Please check the console for more details.");
      return;
    }

    const listingData = {
      title,
      description,
      price: parseFloat(finalPrice),
      image_url: imageUrl,
      display_name: user.displayName,
      email: user.email,
      category,
      // availability_dates: isRenting ? availabilityDates : null,
      availability_dates: `${startDate.toLocaleDateString()} to ${endDate.toLocaleDateString()}`,
      type: isRenting ? 'rent' : 'sale',
      user_id: user.uid, 
      email: user.email,
      display_name: user.displayName,
      trans_comp: false,
    };

    try {
      const response = await fetch('/api/sell-list/upload', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(listingData)
      });

      const data = await response.json();
      if (response.ok) {
        alert('Listing added successfully!');
        resetForm();
      } else {
        alert('Failed to add listing: ' + data.message);
      }
    } catch (error) {
      console.error('Failed to add listing:', error);
      alert('An error occurred. Please try again.');
    }
  };

  const fetchListings = async () => {
    console.log("we fetch listings (not shown for some reason)")
    console.log(user.displayName)
    try {
      const response = await fetch(`/api/sell-list/user-listings/${user.uid}`);
      const data = await response.json();
      if (response.ok) {
        setListings(data);
      } else {
        console.error("Failed to fetch listings:", data);
        alert("Failed to fetch listings. Please try again.");
      }
    } catch (error) {
      console.error("Failed to fetch listings:", error);
      alert("An error occurred while fetching listings. Please check your network connection and try again.");
    }
  };

  const updateListing = async () => {
    if (!selectedListingId) {
      alert("You must choose a listing to update.");
      return;
    }

    const finalPrice = validateFormAndUser(title, price, user);
    if (finalPrice === null) {
      return;
    }

    let imageUrl = imagePreviewUrl;  // Use the existing image URL if not uploading a new one

    if (image) {  // If there's a new image, upload it and get the new URL
      try {
        const imageResponse = await fetch(
          `/api/sell-list/upload-image/${user.uid}`,
          {
            method: "POST",
            body: formData, // Send the file as FormData
          }
        );

        if (!imageResponse.ok) {
          throw new Error("Image upload failed");
        }

        const imageData = await imageResponse.json();
        imageUrl = imageData.image_url; // Update the imageUrl with the new one
      } catch (error) {
        console.error("Failed to fetch:", error);
        if (error.response) {
          error.response.json().then((json) => {
            console.log("Error details:", json);
          });
        }
        alert("An error occurred. Please check the console for more details.");
        return;
      }
    }

    const requestData = {
      title: title,
      description: description,
      price: parseFloat(finalPrice),
      image_url: imageUrl,
      category: category,
      // availability_dates: isRenting ? availabilityDates : null,
      availability_dates: `${startDate.toLocaleDateString()} to ${endDate.toLocaleDateString()}`,
      type: isRenting ? 'rent' : 'sale',
      display_name: user.displayName,
      user_id: user.uid,
    };

    try {
      const response = await fetch(`/api/sell-list/update/${selectedListingId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });

      const data = await response.json();
      if (response.ok) {
        alert("Listing updated successfully!");
        resetForm();
      } else {
        alert("Failed to update listing: " + data.message);
      }
    } catch (error) {
      console.error("Failed to update:", error);
      alert("An error occurred. Please try again.");
    }
  };

  const deleteListing = async () => {
    if (!selectedListingId) {
      alert("You must choose a listing to delete.");
      return;
    }

    if (!window.confirm("Are you sure you want to delete this listing?")) {
      return;
    }

    try {
      const response = await fetch(`/api/sell-list/delete/${selectedListingId}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        alert("Listing deleted successfully!");
        resetForm();
      } else {
        const errorData = await response.json();
        alert(`Failed to delete listing: ${errorData.message}`);
      }
    } catch (error) {
      console.error("Failed to delete:", error);
      alert("An error occurred during deletion. Please try again.");
    }
  };

  return (
    <>
      <div style={{ paddingBottom: "100px" }}>
        <div style={{ textAlign: "center", margin: "20px 0" }}>
          <h1>Sell or Rent Your Item</h1>
        </div>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            marginBottom: "10px",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-around",
              width: "100%",
              maxWidth: "500px",
              marginBottom: "5px",
            }}
          >
            <button
              onClick={() => setActiveTab("upload")}
              style={{
                padding: "10px 20px",
                width: "48%",
                backgroundColor: activeTab === "upload" ? "#007BFF" : "#ccc",
                color: "white",
                border: "none",
                borderRadius: "4px",
              }}
            >
              Upload New Listing
            </button>
            <button
              onClick={() => setActiveTab("update")}
              style={{
                padding: "10px 20px",
                width: "48%",
                backgroundColor: activeTab === "update" ? "#28a745" : "#ccc",
                color: "white",
                border: "none",
                borderRadius: "4px",
              }}
            >
              Update Existing Listing
            </button>
          </div>
          <div
            style={{
              display: "flex",
              justifyContent: "space-around",
              width: "100%",
              maxWidth: "500px",
            }}
          >
            <button
              onClick={() => setActiveTab("delete")}
              style={{
                padding: "10px 20px",
                width: "48%",
                backgroundColor: activeTab === "delete" ? "#dc3545" : "#ccc",
                color: "white",
                border: "none",
                borderRadius: "4px",
              }}
            >
              Delete Existing Listing
            </button>
            <button
              onClick={fetchListings}
              style={{
                padding: "10px 20px",
                width: "48%",
                backgroundColor: "#6c757d",
                color: "white",
                border: "none",
                borderRadius: "4px",
              }}
            >
              Fetch My Listings
            </button>
          </div>
        </div>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "20px",
            maxWidth: "500px",
            margin: "0 auto",
            padding: "20px",
            boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
            borderRadius: "8px",
            backgroundColor: "#fff",
          }}
        >
          {activeTab !== "upload" && (
            <div>
              <select
                value={selectedListingId}
                onChange={(e) => setSelectedListingId(e.target.value)}
                style={{
                  padding: "11px",
                  fontSize: "16px",
                  width: "100%",
                  marginBottom: "-10px",
                  border: "1px solid #ccc",
                  borderRadius: "4px",
                }}
              >
                <option value="">Select a listing first</option>
                {listings.map((listing) => (
                  <option key={listing.listing_id} value={listing.listing_id}>
                    {listing.title}
                  </option>
                ))}
              </select>
            </div>
          )}
          <div>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Title (Required)"
              style={{
                padding: '10px',
                fontSize: '16px',
                border: '1px solid #ccc',
                borderRadius: '4px',
                width: '100%',
              }}
            />
          </div>

          <div>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Description (Optional)"
              style={{
                height: '100px',
                padding: '10px',
                fontSize: '16px',
                border: '1px solid #ccc',
                borderRadius: '4px',
                width: '100%',
                resize: 'none',
              }}
            />
          </div>

          <div>
            <input
              type="text"
              value={price}
              onChange={handlePriceChange}
              placeholder="Price (Required)"
              style={{
                padding: '10px',
                fontSize: '16px',
                border: '1px solid #ccc',
                borderRadius: '4px',
                width: '100%',
              }}
            />
          </div>

          <div>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              style={{
                padding: '10px',
                fontSize: '16px',
                border: '1px solid #ccc',
                borderRadius: '4px',
                width: '100%',
              }}
            >
              <option value="All">All</option>
              <option value="Food">Food</option>
              <option value="Electronics">Electronics</option>
              <option value="Furniture">Furniture</option>
              <option value="Clothing">Clothing</option>
            </select>
          </div>

          {isRenting && (
            <div>
              <label style={{ marginBottom: '10px', fontSize: '16px', display: 'block' }}>Availability Dates (For Rent Only)</label>
              <DatePicker
                selected={startDate}
                onChange={(dates) => {
                  const [start, end] = dates;
                  setStartDate(start);
                  setEndDate(end);
                }}
                startDate={startDate}
                endDate={endDate}
                selectsRange
                inline
                style={{
                  padding: '10px',
                  fontSize: '16px',
                  border: '1px solid #ccc',
                  borderRadius: '4px',
                  width: '100%',
                }}
              />
            </div>
          )}

          <div>
            <label>
              <input
                type="checkbox"
                checked={isRenting}
                onChange={(e) => setIsRenting(e.target.checked)}
              /> Is this item for rent?
            </label>
          </div>

          <div>
            <input
              type="file"
              onChange={handleImageChange}
              accept="image/*"
              style={{
                padding: '10px',
                fontSize: '16px',
                border: '1px solid #ccc',
                borderRadius: '4px',
                width: '100%',
              }}
            />
          </div>

          {imagePreviewUrl && (
            <div>
              <img src={imagePreviewUrl} alt="Preview" style={{ maxWidth: '100%', marginTop: '20px' }} />
            </div>
          )}

          <div>
            <button onClick={uploadListing} style={{
              padding: '10px 20px',
              fontSize: '16px',
              backgroundColor: '#007BFF',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              width: '100%',
            }}>
              List Item
            </button>
          </div>

          {activeTab === "update" && (
            <button onClick={updateListing} style={{
              padding: '10px 20px',
              fontSize: '16px',
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}>
              Update Listing
            </button>
          )}
          {activeTab === "delete" && (
            <button onClick={deleteListing} style={{
              padding: '10px 20px',
              fontSize: '16px',
              backgroundColor: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}>
              Delete Listing
            </button>
          )}
        </div>
      </div>
    </>
  );
}
