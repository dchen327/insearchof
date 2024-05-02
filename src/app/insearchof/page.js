"use client";
import { auth, storage } from "../firebase/config";
import { useEffect, useState } from "react";
import { onAuthStateChanged } from "firebase/auth";
import { useRouter } from "next/navigation";
import Image from 'next/image';

export default function Page() {
  // State management for various component functionalities
  const [user, setUser] = useState(null);
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [image, setImage] = useState(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState("");
  const [urgent, setUrgent] = useState(false);
  const [items, setItems] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [activeTab, setActiveTab] = useState("upload");
  const [tooltipVisible, setTooltipVisible] = useState({
    title: false,
    description: false,
    price: false,
    image: false,
    urgent: false,
  });
  const [selectedItemId, setSelectedItemId] = useState("");
  const [transactionStatus, setTransactionStatus] = useState(null);

  // Monitor authentication state changes
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

  // Reset form fields whenever the active tab changes
  useEffect(() => {
    resetForm(); // Resets all form-related states
  }, [activeTab]);

  // Validate form inputs before submission
  function validateFormAndUser(title, price, user) {
    if (!title) {
      alert("Title is required.");
      return null;
    }
    const finalPrice = price === "" ? 0 : parseFloat(price);
    if (isNaN(finalPrice) || finalPrice < 0) {
      alert("Price must be a valid number and cannot be negative.");
      return null;
    }
    if (!user) {
      alert("You need to be logged in to submit a request.");
      return null;
    }
    return finalPrice;
  }

  // Clear all form fields
  function resetForm() {
    setTitle("");
    setDescription("");
    setPrice("");
    setImage(null);
    setImagePreviewUrl("");
    setUrgent(false);
    setSelectedCategories([]);
    setSelectedItemId("");
  }

  // Fetch list of user's uploaded items for selection
  const handleDropdownClick = async () => {
    if (user) {
      try {
        const response = await fetch(`/api/insearchof/user-items/${user.uid}`);
        const data = await response.json();
        if (response.ok) {
          if (data.length === 0) {
            alert("You have no items uploaded. Please upload an item first.");
          } else {
            setItems(data);
          }
        } else {
          console.error("Failed to fetch items:", data);
          alert("Failed to fetch items. Please try again.");
        }
      } catch (error) {
        console.error("Failed to fetch items:", error);
        alert(
          "An error occurred while fetching items. Please check your network connection and try again."
        );
      }
    }
  };

  // Handle item selection from dropdown, fetching its details to autofill form for updates
  const handleItemSelection = async (e) => {
    const itemId = e.target.value;
    setSelectedItemId(itemId);

    try {
      const response = await fetch(`/api/insearchof/item-details/${itemId}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();
      if (response.ok) {
        // Fill in the form with the details fetched
        setTitle(data.itemDetails.title);
        setDescription(data.itemDetails.description);
        setPrice(data.itemDetails.price.toString());
        setImagePreviewUrl(data.itemDetails.image_url);
        setUrgent(data.itemDetails.urgent);
        setSelectedCategories(data.itemDetails.categories);
        setTransactionStatus(data.itemDetails.trans_comp); // Store the transaction completion status
      } else {
        console.error("Item details fetch error:", data.message);
        resetForm();
      }
    } catch (error) {
      console.error("Failed to fetch item details:", error);
      resetForm();
    }
  };

  // Manage tab switching logic for UI
  const handleTabChange = (tabName) => {
    setActiveTab(tabName);
  };

  // Handle image file input and generate preview
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
      setImagePreviewUrl("");
    }
  };

  // Validate and format price input to prevent invalid characters
  const handlePriceChange = (e) => {
    const value = e.target.value;

    // prevent any non-numeric characters from being entered
    // allow only one decimal point
    const validValue = value.replace(/[^0-9.]/g, "").replace(/(\..*)\./g, "$1");
    const parts = validValue.split(".");

    // allow only two decimal places max
    if (parts.length > 1) {
      parts[1] = parts[1].substring(0, 2);
    }
    const formattedValue = parts.join(".");
    setPrice(formattedValue);
  };

  // Handle image upload to server
  const uploadImage = async (imageFile) => {
    if (!imageFile) {
      // no image provided
      return "";
    }

    const formData = new FormData();
    formData.append("file", imageFile);

    const imageResponse = await fetch(
      `/api/insearchof/upload-image/${user.uid}`,
      {
        method: "POST",
        body: formData, // Send the file as FormData
      }
    );

    if (!imageResponse.ok) {
      throw new Error("Image upload failed");
    }

    const imageData = await imageResponse.json();
    return imageData.image_url; // Return the uploaded image URL
  };

  // Handle image deletion from server
  const deleteImage = async (filename, user_id) => {
    try {
      const response = await fetch(
        `/api/insearchof/delete-image/${filename}/${user_id}`,
        {
          method: "DELETE",
          headers: { "Content-Type": "application/json" },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to delete image.");
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Failed to delete image:", error);
      alert("An error occurred while deleting the image. Please try again.");
      return null;
    }
  };

  // Submit new request upload
  const uploadRequest = async () => {
    const finalPrice = validateFormAndUser(title, price, user);
    if (finalPrice === null) {
      return;
    }

    // Upload the image first, if it exists
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

      const requestData = {
        title: title,
        description: description,
        price: parseFloat(finalPrice),
        image_url: imageUrl,
        type: "request",
        trans_comp: false,
        display_name: user.displayName,
        email: user.email,
        user_id: user.uid,
        urgent: urgent,
        categories: selectedCategories,
      };

      // Send the request data to the backend
      const response = await fetch("api/insearchof/upload", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });

      const data = await response.json();
      if (response.ok) {
        alert("Request uploaded successfully!");
        resetForm();
      } else {
        alert("Failed to upload request: " + data.message);
      }
    } catch (error) {
      console.error("Failed to fetch:", error);
      alert("An error occurred. Please try again.");
    }
  };

  // Update existing request details
  const updateRequest = async () => {
    if (!selectedItemId) {
      alert("You must choose an item to update.");
      return;
    }

    const finalPrice = validateFormAndUser(title, price, user);
    if (finalPrice === null) {
      return;
    }

    try {
      // Fetch current item details including the image_url from the database
      const itemDetailsResponse = await fetch(
        `/api/insearchof/item-details/${selectedItemId}`
      );
      if (!itemDetailsResponse.ok) {
        throw new Error("Failed to fetch item details.");
      }
      const itemDetails = await itemDetailsResponse.json();
      let imageUrl = itemDetails.itemDetails.image_url; // Retrieve the current image URL from the item details

      // If there is a new image to upload, handle the previous image's deletion and upload the new one
      if (image) {
        if (imageUrl) {
          const filenameToDelete = imageUrl.split("/").pop();
          await deleteImage(filenameToDelete, user.uid);
        }

        try {
          imageUrl = await uploadImage(image);
        } catch (error) {
          console.error("Image upload failed:", error);
          alert("Failed to upload new image. Please try again.");
          return;
        }
      }

      // Prepare the request data for updating the item
      const requestData = {
        title: title,
        description: description,
        price: parseFloat(price),
        image_url: imageUrl,
        type: "request",
        trans_comp: false,
        user_id: user.uid,
        display_name: user.displayName,
        email: user.email,
        urgent: urgent,
        categories: selectedCategories, // Include selected categories
      };

      // Send the update request to the backend
      const response = await fetch(`/api/insearchof/update/${selectedItemId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestData),
      });

      const data = await response.json();
      if (response.ok) {
        alert("Request updated successfully!");
        resetForm();
      } else {
        alert("Failed to update request: " + data.message);
      }
    } catch (error) {
      console.error("Failed to update:", error);
      alert("An error occurred. Please try again.");
    }
  };

  // Delete an existing request
  const deleteRequest = async () => {
    if (!selectedItemId) {
      alert("You must choose an item to delete.");
      return;
    }

    if (!window.confirm("Are you sure you want to delete this request?")) {
      return;
    }

    try {
      const response = await fetch(`/api/insearchof/delete/${selectedItemId}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_id: user.uid }), // Send necessary data if needed, e.g., user ID
      });

      if (response.ok) {
        alert("Request deleted successfully!");
        resetForm();
      } else {
        const errorData = await response.json();
        alert(`Failed to delete request: ${errorData.message}`);
      }
    } catch (error) {
      console.error("Failed to delete:", error);
      alert("An error occurred during deletion. Please try again.");
    }
  };

  // Mark a transaction as complete
  const markTransactionComplete = async () => {
    if (!selectedItemId) {
      alert("You must choose an item to mark as complete.");
      return;
    }

    try {
      const response = await fetch(`/api/insearchof/mark/${selectedItemId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_id: user.uid }),
      });
      const data = await response.json();
      if (response.ok) {
        setTransactionStatus(data.trans_comp_value); // Update the transaction status in state
        alert(
          `You marked this request as ${data.trans_comp_value ? "complete" : "incomplete"
          }`
        );
      } else {
        alert("Failed to mark transaction as complete: " + data.message);
      }
    } catch (error) {
      console.error("Failed to mark transaction as complete:", error);
      alert(
        "An error occurred while marking transaction as complete. Please try again."
      );
    }
  };

  // Toggle urgent status
  const toggleUrgent = () => {
    setUrgent(!urgent);
  };

  // Display tooltips for form fields
  const toggleTooltip = (field) => {
    setTooltipVisible((prev) => ({ ...prev, [field]: !prev[field] }));
  };

  // Tooltip component for displaying hints
  const Tooltip = ({ show, text }) =>
    show ? (
      <div
        style={{
          position: "absolute",
          backgroundColor: "#f0f0f0",
          border: "1px solid #ccc",
          padding: "10px",
          borderRadius: "4px",
          boxShadow: "0 2px 5px rgba(0,0,0,0.2)",
          zIndex: "10",
          marginTop: "0px",
          width: "200px",
        }}
      >
        {text}
      </div>
    ) : null;

  // Manage category selection for requests
  const toggleCategory = (category) => {
    if (selectedCategories.includes(category)) {
      setSelectedCategories(selectedCategories.filter((c) => c !== category));
    } else {
      setSelectedCategories([...selectedCategories, category]);
    }
  };

  // Component for displaying category checkboxes
  function CategoriesDisplay({ selectedCategories, toggleCategory, disabled }) {
    const categories = ["Food", "Electronics", "Furniture", "Clothing"];
    return (
      <div>
        <div style={{ marginBottom: "10px", fontSize: "16px" }}>
          Categories
          <div style={{ display: "flex", flexWrap: "wrap", gap: "5px" }}>
            {categories.map((category, index) => (
              <label
                key={index}
                style={{
                  marginRight: "10px",
                  fontSize: "16px",
                  display: "flex",
                  alignItems: "center",
                }}
              >
                <input
                  type="checkbox"
                  checked={selectedCategories.includes(category)}
                  onChange={() => toggleCategory(category)}
                  disabled={disabled} // Use the disabled prop here
                />
                <span style={{ marginLeft: "5px" }}>{category}</span>
              </label>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <div style={{ paddingBottom: "100px" }}>
        <div style={{ textAlign: "center", margin: "20px 0" }}>
          <h1>ISO Request</h1>
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
              onClick={() => handleTabChange("upload")}
              style={{
                padding: "10px 20px",
                width: "48%",
                backgroundColor: activeTab === "upload" ? "#007BFF" : "#ccc",
                color: "white",
                border: "none",
                borderRadius: "4px",
              }}
            >
              Upload New Request
            </button>
            <button
              onClick={() => handleTabChange("update")}
              style={{
                padding: "10px 20px",
                width: "48%",
                backgroundColor: activeTab === "update" ? "#28a745" : "#ccc",
                color: "white",
                border: "none",
                borderRadius: "4px",
              }}
            >
              Update Existing Request
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
              onClick={() => handleTabChange("delete")}
              style={{
                padding: "10px 20px",
                width: "48%",
                backgroundColor: activeTab === "delete" ? "#dc3545" : "#ccc",
                color: "white",
                border: "none",
                borderRadius: "4px",
              }}
            >
              Delete Existing Request
            </button>
            <button
              onClick={() => handleTabChange("complete")}
              style={{
                padding: "10px 20px",
                width: "48%",
                backgroundColor: activeTab === "complete" ? "#6c757d" : "#ccc",
                color: "white",
                border: "none",
                borderRadius: "4px",
              }}
            >
              Mark Request Complete
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
                value={selectedItemId}
                onClick={handleDropdownClick}
                onChange={handleItemSelection}
                style={{
                  padding: "11px",
                  fontSize: "16px",
                  width: "100%",
                  marginBottom: "-10px",
                  border: "1px solid #ccc",
                  borderRadius: "4px",
                }}
              >
                <option value="">Select an item first</option>
                {items.map((item) => (
                  <option key={item.item_id} value={item.item_id}>
                    {item.title}
                  </option>
                ))}
              </select>
            </div>
          )}
          {activeTab === "upload" && (
            <div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  marginBottom: "10px",
                }}
              >
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Title (Required)"
                  style={{
                    padding: "10px",
                    fontSize: "16px",
                    border: "1px solid #ccc",
                    borderRadius: "4px",
                    flexGrow: 1,
                    marginRight: "5px",
                  }}
                />
                <button
                  onClick={() => toggleTooltip("title")}
                  style={{ padding: "0 5px", fontSize: "16px" }}
                >
                  ?
                </button>
              </div>
              <Tooltip
                show={tooltipVisible.title}
                text="Enter the title of the request."
              />

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  marginBottom: "10px",
                }}
              >
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Description (Optional)"
                  style={{
                    height: "100px",
                    padding: "10px",
                    fontSize: "16px",
                    border: "1px solid #ccc",
                    borderRadius: "4px",
                    flexGrow: 1,
                    marginRight: "5px",
                  }}
                />
                <button
                  onClick={() => toggleTooltip("description")}
                  style={{ padding: "0 5px", fontSize: "16px" }}
                >
                  ?
                </button>
              </div>
              <Tooltip
                show={tooltipVisible.description}
                text="Provide a description for your request."
              />

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  marginBottom: "10px",
                }}
              >
                <input
                  type="text"
                  value={price}
                  onChange={handlePriceChange}
                  placeholder="Price (Optional)"
                  style={{
                    padding: "10px",
                    fontSize: "16px",
                    border: "1px solid #ccc",
                    borderRadius: "4px",
                    flexGrow: 1,
                    marginRight: "5px",
                  }}
                />
                <button
                  onClick={() => toggleTooltip("price")}
                  style={{ padding: "0 5px", fontSize: "16px" }}
                >
                  ?
                </button>
              </div>
              <Tooltip
                show={tooltipVisible.price}
                text="Specify the price you are willing to pay. Leave empty for no specific price."
              />

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  marginBottom: "10px",
                }}
              >
                <input
                  type="file"
                  onChange={handleImageChange}
                  accept="image/*"
                  style={{
                    padding: "8px",
                    fontSize: "16px",
                    border: "1px solid #ccc",
                    borderRadius: "4px",
                    flexGrow: 1,
                    marginRight: "5px",
                  }}
                />
                <button
                  onClick={() => toggleTooltip("image")}
                  style={{ padding: "0 5px", fontSize: "16px" }}
                >
                  ?
                </button>
              </div>
              <Tooltip
                show={tooltipVisible.image}
                text="Upload an image related to your request."
              />

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  marginBottom: "10px",
                }}
              >
                <button
                  onClick={toggleUrgent}
                  style={{
                    padding: "10px",
                    fontSize: "16px",
                    border: "1px solid #ccc",
                    borderRadius: "4px",
                    backgroundColor: urgent ? "#FF0000" : "#FFFFFF",
                    color: urgent ? "#FFFFFF" : "#000000",
                    flexGrow: 1,
                    marginRight: "5px",
                  }}
                >
                  Urgent
                </button>
                <button
                  onClick={() => toggleTooltip("urgent")}
                  style={{ padding: "0 5px", fontSize: "16px" }}
                >
                  ?
                </button>
              </div>
              <Tooltip
                show={tooltipVisible.urgent}
                text="Mark this request as urgent if it needs immediate attention."
              />

              <CategoriesDisplay
                selectedCategories={selectedCategories}
                toggleCategory={toggleCategory}
              />
              {imagePreviewUrl && (
                <Image
                  src={imagePreviewUrl}
                  alt="Preview"
                  width={500} // specify width
                  height={300} // specify height
                  layout="responsive" // this will maintain the aspect ratio
                />
              )}
              <button
                onClick={uploadRequest}
                style={{
                  padding: "10px 20px",
                  fontSize: "16px",
                  backgroundColor: "#007BFF",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  width: "100%",
                  marginTop: "10px",
                }}
              >
                Upload Request
              </button>
            </div>
          )}
          {activeTab === "update" && (
            <div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  marginBottom: "10px",
                }}
              >
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Title (Required)"
                  style={{
                    padding: "10px",
                    fontSize: "16px",
                    border: "1px solid #ccc",
                    borderRadius: "4px",
                    flexGrow: 1,
                    marginRight: "5px",
                  }}
                  disabled={!selectedItemId} // Disable if no item is selected
                />
                <button
                  onClick={() => toggleTooltip("title")}
                  disabled={!selectedItemId}
                  style={{ padding: "0 5px", fontSize: "16px" }}
                >
                  ?
                </button>
              </div>
              <Tooltip
                show={tooltipVisible.title}
                text="Enter the title of the request."
              />

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  marginBottom: "10px",
                }}
              >
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Description (Optional)"
                  style={{
                    height: "100px",
                    padding: "10px",
                    fontSize: "16px",
                    border: "1px solid #ccc",
                    borderRadius: "4px",
                    flexGrow: 1,
                    marginRight: "5px",
                  }}
                  disabled={!selectedItemId} // Disable if no item is selected
                />
                <button
                  onClick={() => toggleTooltip("description")}
                  disabled={!selectedItemId}
                  style={{ padding: "0 5px", fontSize: "16px" }}
                >
                  ?
                </button>
              </div>
              <Tooltip
                show={tooltipVisible.description}
                text="Provide a description for your request."
              />

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  marginBottom: "10px",
                }}
              >
                <input
                  type="text"
                  value={price}
                  onChange={handlePriceChange}
                  placeholder="Price (Optional)"
                  style={{
                    padding: "10px",
                    fontSize: "16px",
                    border: "1px solid #ccc",
                    borderRadius: "4px",
                    flexGrow: 1,
                    marginRight: "5px",
                  }}
                  disabled={!selectedItemId} // Disable if no item is selected
                />
                <button
                  onClick={() => toggleTooltip("price")}
                  disabled={!selectedItemId}
                  style={{ padding: "0 5px", fontSize: "16px" }}
                >
                  ?
                </button>
              </div>
              <Tooltip
                show={tooltipVisible.price}
                text="Specify the price you are willing to pay. Leave empty for no specific price."
              />

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  marginBottom: "10px",
                }}
              >
                <label style={{ flexGrow: 1, marginRight: "5px" }}>
                  <input
                    type="file"
                    onChange={handleImageChange}
                    accept="image/*"
                    style={{
                      padding: "8px",
                      fontSize: "16px",
                      border: "1px solid #ccc",
                      borderRadius: "4px",
                      width: "100%",
                    }}
                    disabled={!selectedItemId} // Disable if no item is selected
                  />
                </label>
                <button
                  onClick={() => toggleTooltip("image")}
                  disabled={!selectedItemId}
                  style={{ padding: "0 5px", fontSize: "16px" }}
                >
                  ?
                </button>
              </div>
              <Tooltip
                show={tooltipVisible.image}
                text="Upload an image related to your request."
              />

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  marginBottom: "10px",
                }}
              >
                <button
                  onClick={toggleUrgent}
                  style={{
                    padding: "10px",
                    fontSize: "16px",
                    border: "1px solid #ccc",
                    borderRadius: "4px",
                    backgroundColor: urgent ? "#FF0000" : "#FFFFFF",
                    color: urgent ? "#FFFFFF" : "#000000",
                    flexGrow: 1,
                    marginRight: "5px",
                  }}
                  disabled={!selectedItemId} // Disable if no item is selected
                >
                  Urgent
                </button>
                <button
                  onClick={() => toggleTooltip("urgent")}
                  disabled={!selectedItemId}
                  style={{ padding: "0 5px", fontSize: "16px" }}
                >
                  ?
                </button>
              </div>
              <Tooltip
                show={tooltipVisible.urgent}
                text="Mark this request as urgent if it needs immediate attention."
              />

              <CategoriesDisplay
                selectedCategories={selectedCategories}
                toggleCategory={toggleCategory}
                disabled={!selectedItemId} // Pass disabled based on whether an item is selected
              />
              {imagePreviewUrl && (
                <Image
                  src={imagePreviewUrl}
                  alt="Preview"
                  width={500} // specify width
                  height={300} // specify height
                  layout="responsive" // this will maintain the aspect ratio
                />
              )}
              <button
                onClick={updateRequest}
                style={{
                  padding: "10px 20px",
                  fontSize: "16px",
                  backgroundColor: "#28a745",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  width: "100%",
                  marginTop: "10px",
                }}
                disabled={!selectedItemId}
              >
                Update Request
              </button>
            </div>
          )}{" "}
          {activeTab === "delete" && (
            <div>
              <button
                onClick={deleteRequest}
                style={{
                  padding: "10px 20px",
                  fontSize: "16px",
                  backgroundColor: "#dc3545",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  width: "100%",
                }}
              >
                Delete Request
              </button>
            </div>
          )}
          {activeTab === "complete" && (
            <div>
              {selectedItemId && transactionStatus !== null && (
                <div style={{ fontSize: "16px", marginBottom: "5px" }}>
                  {`The item "${title}" is currently marked as `}
                  {transactionStatus ? "complete" : "incomplete"}.
                </div>
              )}
              <button
                onClick={markTransactionComplete}
                style={{
                  padding: "10px 20px",
                  fontSize: "16px",
                  backgroundColor: "#6c757d",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  width: "100%",
                }}
              >
                Mark Request
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
