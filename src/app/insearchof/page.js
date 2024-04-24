"use client";
import { auth, storage } from "../firebase/config";
import { useEffect, useState } from "react";
import { onAuthStateChanged } from "firebase/auth";
import { useRouter } from "next/navigation";

export default function Page() {
  const [user, setUser] = useState(null);
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [item_id, setItem_id] = useState(""); // DELETE THIS LINE
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [image, setImage] = useState(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState("");
  const [showTitleTooltip, setShowTitleTooltip] = useState(false);
  const [showDescriptionTooltip, setShowDescriptionTooltip] = useState(false);
  const [showPriceTooltip, setShowPriceTooltip] = useState(false);
  const [showImageTooltip, setShowImageTooltip] = useState(false);
  const [urgent, setUrgent] = useState(false);
  const [showUrgentTooltip, setShowUrgentTooltip] = useState(false);
  const [selectedCategories, setSelectedCategories] = useState([]);

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

  function resetForm() {
    setItem_id("");
    setTitle("");
    setDescription("");
    setPrice("");
    setImage(null);
    setImagePreviewUrl("");
    setUrgent(false);
    setSelectedCategories([]);
  }

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

  const handleItemIDChange = async (e) => {
    const newItemId = e.target.value;
    setItem_id(newItemId);

    if (newItemId.length === 20) {
      // length of item id
      try {
        const response = await fetch(
          `/api/insearchof/validate-item-id/${newItemId}/${user.uid}`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
          }
        );

        const data = await response.json();
        if (response.ok && data.isValid) {
          // fill in form
          setTitle(data.itemDetails.title);
          setDescription(data.itemDetails.description);
          setPrice(data.itemDetails.price.toString());
          setImagePreviewUrl(data.itemDetails.image_url);
          setUrgent(data.itemDetails.urgent);
          setSelectedCategories(data.itemDetails.categories);
        } else {
          console.error("Item ID validation error:", data.message);
          resetForm();
        }
      } catch (error) {
        console.error("Failed to validate Item ID:", error);
        resetForm();
      }
    } else {
      resetForm();
    }
  };

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

  const updateRequest = async () => {
    if (!item_id) {
      alert("No item ID provided for the update.");
      return;
    }

    const finalPrice = validateFormAndUser(title, price, user);
    if (finalPrice === null) {
      return;
    }

    try {
      // Fetch current item details including the image_url from the database
      const itemDetailsResponse = await fetch(
        `/api/insearchof/item-details/${item_id}`
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
        urgent: urgent,
        categories: selectedCategories, // Include selected categories
      };

      // Send the update request to the backend
      const response = await fetch(`/api/insearchof/update/${item_id}`, {
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

  const deleteRequest = async () => {
    if (!item_id) {
      alert("No item ID provided for the deletion.");
      return;
    }

    if (!window.confirm("Are you sure you want to delete this request?")) {
      return;
    }

    try {
      const response = await fetch(`/api/insearchof/delete/${item_id}`, {
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

  const markTransactionComplete = async () => {
    if (!item_id) {
      alert("No item ID provided for the update.");
      return;
    }

    try {
      const response = await fetch(`/api/insearchof/mark/${item_id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_id: user.uid }),
      });
      const data = await response.json();
      console.log(data);
      if (response.ok) {
        alert(`Transaction Complete is now ${data["trans_comp_value"]}`);
      } else {
        alert("Failed to mark transaction as complete: " + data.message);
      }
    } catch (error) {
      // network failure?
      console.error("Failed to mark transaction as complete:", error);
      alert(
        "An error occurred while marking transaction as complete. Please try again."
      );
    }
  };

  const toggleUrgent = () => {
    setUrgent(!urgent);
  };

  const categories = ["Food", "Electronics", "Furniture", "Clothing"];

  const toggleCategory = (category) => {
    if (selectedCategories.includes(category)) {
      setSelectedCategories(selectedCategories.filter((c) => c !== category));
    } else {
      setSelectedCategories([...selectedCategories, category]);
    }
  };

  const tooltipStyle = {
    position: "absolute",
    top: "100%",
    left: "0",
    width: "75%", // Tooltip covers 75% of the input field
    backgroundColor: "#f0f0f0",
    padding: "10px",
    borderRadius: "4px",
    boxShadow: "0 2px 5px rgba(0,0,0,0.2)",
    zIndex: "100",
    marginTop: "5px",
  };

  return (
    <>
      <div
        style={{
          textAlign: "center",
          margin: "20px 0",
        }}
      >
        <h1>ISO Requester</h1>
      </div>

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "20px",
          maxWidth: "500px",
          margin: "0px auto",
          padding: "20px",
          boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
          borderRadius: "8px",
          backgroundColor: "#fff",
        }}
      >
        {["item id", "title", "description", "price", "image", "urgent"].map(
          (field) => (
            // ITEM ID IS TEMPORARY, PLEASE DELETE
            <div
              key={field}
              style={{
                position: "relative",
                display: "flex",
                alignItems: "center",
                gap: "5px",
              }}
            >
              {field === "item id" && (
                <input
                  type="text"
                  value={item_id}
                  onChange={handleItemIDChange}
                  placeholder="Item ID (Temporary)"
                  style={{
                    padding: "10px",
                    fontSize: "16px",
                    border: "1px solid #ccc",
                    borderRadius: "4px",
                    flexGrow: 1,
                  }}
                />
              )}

              {field === "title" && (
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
                  }}
                />
              )}
              {field === "description" && (
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
                    resize: "none",
                  }}
                />
              )}
              {field === "price" && (
                <>
                  <label style={{ marginRight: "5px", fontSize: "16px" }}>
                    $
                  </label>
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
                    }}
                  />
                </>
              )}
              {field === "image" && (
                <div style={{ position: "relative" }}>
                  <label
                    style={{
                      flexGrow: 1,
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "flex-start",
                    }}
                  >
                    <span style={{ marginBottom: "10px", fontSize: "16px" }}>
                      Image (optional)
                    </span>
                    <input
                      type="file"
                      onChange={handleImageChange}
                      accept="image/*"
                      style={{
                        padding: "10px",
                        fontSize: "16px",
                        border: "1px solid #ccc",
                        borderRadius: "4px",
                        width: "100%", // Ensure the input takes the full width of its parent container
                      }}
                    />
                  </label>
                  {/* Urgent button below the image file input */}
                </div>
              )}
              {field === "urgent" && (
                <div>
                  <button
                    onClick={toggleUrgent}
                    style={{
                      padding: "10px",
                      fontSize: "16px",
                      border: "1px solid #ccc",
                      borderRadius: "4px",
                      backgroundColor: urgent ? "#FF0000" : "#FFFFFF",
                      color: urgent ? "#FFFFFF" : "#000000",
                    }}
                  >
                    Urgent
                  </button>
                </div>
              )}

              <button
                onClick={() => {
                  // Close any open tooltip and open the clicked one
                  setShowTitleTooltip(
                    field === "title" ? !showTitleTooltip : false
                  );
                  setShowDescriptionTooltip(
                    field === "description" ? !showDescriptionTooltip : false
                  );
                  setShowPriceTooltip(
                    field === "price" ? !showPriceTooltip : false
                  );
                  setShowImageTooltip(
                    field === "image" ? !showImageTooltip : false
                  );
                  setShowUrgentTooltip(
                    field === "urgent" ? !showUrgentTooltip : false
                  );
                }}
                style={{ position: "relative", zIndex: "20" }}
              >
                ?
              </button>
              {showTitleTooltip && field === "title" && (
                <div style={tooltipStyle}>
                  The title of item or service requested
                </div>
              )}
              {showDescriptionTooltip && field === "description" && (
                <div style={tooltipStyle}>
                  The description of item or service requested
                </div>
              )}
              {showPriceTooltip && field === "price" && (
                <div style={tooltipStyle}>
                  The price you are willing to pay for such item or service.
                  Leaving it empty also means 0 dollars
                </div>
              )}
              {showImageTooltip && field === "image" && (
                <div style={tooltipStyle}>
                  The image of item or service you are requesting
                </div>
              )}
              {showUrgentTooltip && field === "urgent" && (
                <div style={tooltipStyle}>
                  For items or services needed urgently, preferably within 24
                  hours
                </div>
              )}
            </div>
          )
        )}

        <div style={{ position: "relative" }}>
          <label
            style={{
              flexGrow: 1,
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-start",
            }}
          >
            <span style={{ marginBottom: "10px", fontSize: "16px" }}>
              Categories
            </span>
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
                  />
                  <span style={{ marginLeft: "5px" }}>{category}</span>
                </label>
              ))}
            </div>
          </label>
        </div>

        {imagePreviewUrl && (
          <img
            src={imagePreviewUrl}
            alt="Preview"
            style={{ maxWidth: "100%", marginTop: "20px" }}
          />
        )}
      </div>

      <div
        style={{
          maxWidth: "500px",
          margin: "20px auto",
          display: "flex",
          flexDirection: "column", // Stack the buttons vertically
          alignItems: "center",
          gap: "10px", // Space between buttons
          paddingBottom: "100px", // Add extra space below the buttons for scrolling
          // If the navbar is taller, increase this value accordingly
        }}
      >
        <button
          className="button is-light"
          onClick={uploadRequest}
          style={{
            padding: "10px 20px",
            fontSize: "16px",
            backgroundColor: "#007BFF",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            width: "100%", // Make button full width
          }}
        >
          Upload Request
        </button>
        <button
          className="button is-light"
          onClick={updateRequest}
          style={{
            padding: "10px 20px",
            fontSize: "16px",
            backgroundColor: "#28a745",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            width: "100%", // Make button full width
            marginTop: "10px", // Space above the button
          }}
        >
          Update Request
        </button>
        <button
          className="button is-light"
          onClick={deleteRequest}
          style={{
            padding: "10px 20px",
            fontSize: "16px",
            backgroundColor: "#dc3545",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            width: "100%", // Make button full width
            marginTop: "10px", // Space above the button
          }}
        >
          Delete Request
        </button>
        <button
          className="button is-light"
          onClick={markTransactionComplete}
          style={{
            padding: "10px 20px",
            fontSize: "16px",
            backgroundColor: "#6c757d", // Grey color
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            width: "100%", // Make button full width
            marginTop: "10px", // Space above the button
          }}
        >
          Mark Transaction Complete
        </button>
      </div>
    </>
  );
}
