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

  useEffect(() => {
    if (selectedListingId) {
      fetchListingDetails(selectedListingId);
    }
  }, [selectedListingId]);  // fetch details whenever selectedListingId changes

  // Handles image file input and generate preview
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

  // When user goes to the Upload tab, nothing will be auto-populated.
  // This is useful if they auto-populated info from UPDATE/DELETE.
  const handleSwitchToUploadTab = () => {
    setActiveTab('upload');
    resetForm();
  };

  // Retrieves the price and ensures its correctness using regex
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
    setStartDate("");
    setEndDate("");
  };

  // Handle image upload to server
  const uploadImage = async (imageFile) => {
    if (!imageFile) {
      return ""; // No image provided
    }
  
    const formData = new FormData();
    formData.append("file", imageFile);
  
    try {
      const response = await fetch(
        `/api/sell-list/upload-image/${user.uid}`,
        {
          method: "POST",
          body: formData,
        });
    
      if (!response.ok) {
        const errorText = await response.text(); // Get more error info
        console.error("HTTP error", response.status, errorText);
        throw new Error("Image upload failed: " + errorText);
      }
  
      const imageData = await response.json();
  
      return imageData.image_url;
    } catch (error) {
      console.error("Failed to upload image:", error);
      alert("An error occurred while uploading the image. Please try again.");
      throw error;
    }
  };
  
  //  Uploads a "buy" or "rent" listing with all fields
  const uploadListing = async () => {
    const finalPrice = validateFormAndUser(title, price, user);
    if (finalPrice === null) {
      return;
    }
  
    try {
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
        category,
        availability_dates: isRenting ? `${startDate.toLocaleDateString()} to ${endDate.toLocaleDateString()}` : null,
        type: isRenting ? 'buy' : 'rent',
        user_id: user.uid,
        display_name: user.displayName,
        email: user.email,
        trans_comp: false,
      };
  
      const response = await fetch('/api/sell-list/upload', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
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
  
  // Retrieves information on a singular, specified post
  const fetchListingDetails = async (listingId) => {
    try {
      const response = await fetch(`/api/sell-list/listing-details/${listingId}?user_id=${user.uid}`);
      const data = await response.json();
      if (response.ok) {
        const details = data.listingDetails; // Access the nested listingDetails object
        setTitle(details.title || "");
        setDescription(details.description || "");
        setPrice(details.price.toString() || ""); // Convert price to string to ensure compatibility with input
        setCategory(details.category || "All");
        setIsRenting(details.type === "rent"); // Assuming type indicates if it's renting
        setStartDate(details.availability_dates ? new Date(details.availability_dates.split(" to ")[0]) : new Date());
        setEndDate(details.availability_dates ? new Date(details.availability_dates.split(" to ")[1]) : new Date());
        setImagePreviewUrl(details.image_url || "");
      } else {
        throw new Error(`Failed to fetch details: ${response.status} - ${response.statusText}`);
      }
    } catch (error) {
      console.error("Error fetching listing details:", error);
      alert("Failed to load listing details.");
    }
  };

  // Retrieves information on all posts to allow users to update and delete
  const fetchListings = async () => {
    try {
      const response = await fetch(`/api/sell-list/user-listings/${user.uid}`);
      const data = await response.json();
      if (response.ok) {
        setListings(data);
        alert("All items are now refreshed!");  // Show alert after successful fetch
      } else {
        console.error("Failed to fetch listings:", data);
        alert("Failed to fetch listings. Please try again.");
      }
    } catch (error) {
      console.error("Failed to fetch listings:", error);
      alert("An error occurred while fetching listings. Please check your network connection and try again.");
    }
  };

  // Updates listings with updated values for fields.
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
      title,
      description,
      price: parseFloat(finalPrice),
      image_url: imageUrl, 
      category,
      availability_dates: isRenting ? `${startDate.toISOString().split('T')[0]} to ${endDate.toISOString().split('T')[0]}` : null,
      type: isRenting ? 'rent' : 'buy', 
      user_id: user.uid, 
      display_name: user.displayName, 
      email: user.email, 
      trans_comp: false 
    };

    try {
      const response = await fetch(`/api/sell-list/update/${selectedListingId}?user_id=${user.uid}`, {
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

  // Deletes listing from database
  const deleteListing = async () => {
    if (!selectedListingId) {
      alert("You must choose a listing to delete.");
      return;
    }

    if (!window.confirm("Are you sure you want to delete this listing?")) {
      return;
    }

    try {
      const response = await fetch(`/api/sell-list/delete/${selectedListingId}?user_id=${user.uid}`, {
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
      {/* Main container with extra padding at the bottom */}
      <div style={{ paddingBottom: "100px" }}>
        {/* Title header centered at the top of the page */}
        <div style={{ textAlign: "center", margin: "20px 0" }}>
          <h1>Sell or Rent Your Item</h1>
        </div>
  
        {/* Navigation buttons for switching between different tabs */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            marginBottom: "10px",
          }}
        >
          {/* Tab selection buttons for "Upload" and "Update" */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-around",
              width: "100%",
              maxWidth: "500px",
              marginBottom: "5px",
            }}
          >
            {/* Upload button switches to the "upload" tab */}
            <button
              onClick={handleSwitchToUploadTab}
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
  
            {/* Update button switches to the "update" tab */}
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
  
          {/* Tab selection buttons for "Delete" and "Refresh" */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-around",
              width: "100%",
              maxWidth: "500px",
            }}
          >
            {/* Delete button switches to the "delete" tab */}
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
  
            {/* Refresh button triggers the fetch of all listings */}
            <button
              onClick={fetchListings}
              style={{
                padding: "10px 20px",
                width: "48%",
                backgroundColor: "#ccc",
                color: "white",
                border: "none",
                borderRadius: "4px",
              }}
            >
              Refresh My Listings
            </button>
          </div>
        </div>
  
        {/* Content container for listing form fields */}
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
          {/* Dropdown selection for listings if not in the "upload" tab */}
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
                {/* Default option to prompt user selection */}
                <option value="">Select a listing first</option>
                {/* Populate the dropdown with existing listings */}
                {listings.map((listing) => (
                  <option key={listing.listing_id} value={listing.listing_id}>
                    {listing.title}
                  </option>
                ))}
              </select>
            </div>
          )}
  
          {/* Input field for the listing title */}
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
  
          {/* Textarea for the listing description */}
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
  
          {/* Input field for the listing price */}
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
  
          {/* Dropdown selection for the listing category */}
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
              {/* Options for various item categories */}
              <option value="All">All</option>
              <option value="Food">Food</option>
              <option value="Electronics">Electronics</option>
              <option value="Furniture">Furniture</option>
              <option value="Clothing">Clothing</option>
            </select>
          </div>
  
          {/* Availability date picker if the item is for rent */}
          {isRenting && (
            <div>
              <label style={{ marginBottom: '10px', fontSize: '16px', display: 'block' }}>
                Availability Dates (For Rent Only)
              </label>
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
  
          {/* Checkbox to toggle rental status */}
          <div>
            <label>
              <input
                type="checkbox"
                checked={isRenting}
                onChange={(e) => setIsRenting(e.target.checked)}
              /> Is this item for rent?
            </label>
          </div>
  
          {/* Input field to upload an image file */}
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
  
          {/* Display image preview if available */}
          {imagePreviewUrl && (
            <Image
              src={imagePreviewUrl}
              alt="Preview"
              width={500}
              height={300}
              layout="responsive"
            />
          )}
  
          {/* Button to handle listing creation or update depending on active tab */}
          {activeTab === "upload" && (
            <div>
              <button
                onClick={uploadListing}
                style={{
                  padding: '10px 20px',
                  fontSize: '16px',
                  backgroundColor: '#007BFF',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  width: '100%',
                }}
              >
                List Item
              </button>
            </div>
          )}
  
          {/* Button to update existing listing */}
          {activeTab === "update" && (
            <button
              onClick={updateListing}
              style={{
                padding: '10px 20px',
                fontSize: '16px',
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Update Listing
            </button>
          )}
  
          {/* Button to delete an existing listing */}
          {activeTab === "delete" && (
            <button
              onClick={deleteListing}
              style={{
                padding: '10px 20px',
                fontSize: '16px',
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Delete Listing
            </button>
          )}
        </div>
      </div>
    </>
  );
}


