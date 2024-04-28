"use client";
import { useEffect, useState } from "react";
import { auth, googleProvider } from "../firebase/config";
import { signInWithPopup, signOut, onAuthStateChanged } from "firebase/auth";
import { useRouter } from "next/navigation";

export default function Page() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState([]);
  const [listings, setListings] = useState([]);
  const [transactionHistory, setTransactionHistory] = useState([]);
  const [showPhoneNumberTooltip, setShowPhoneNumberTooltip] = useState(false);
  const [showLocationTooltip, setShowLocationTooltip] = useState(false);
  const [showUserIdTooltip, setShowUserIdTooltip] = useState(false);
  const [showFilterModal, setShowFilterModal] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState("");
  const [location, setLocation] = useState("");
  const [userId, setUserId] = useState("");
  const [locationFilled, setLocationFilled] = useState(false);
  const [listOfItems, setListOfItems] = useState(false);

<<<<<<< HEAD
  const [uploadInfoButton, setShowUploadUserInfoButton] = useState(false);
  const [changeUserButton, setShowChangeUserButton] = useState(false);
  const [showItemModal, setShowItemModal] = useState(false);
  const [showTransactionModal, setShowTransactionModal] = useState(false);
=======
  const [uploadInfoButton, setUploadInfoButtonClicked] = useState(false);

  const [showItemModal, setShowItemModal] = useState(false);
>>>>>>> 113ee4eb2eeac41b0e6866367de36b574e58e64e

  const router = useRouter();

  // performs side effects in function components. subscribes authentication
  // state changes when the component mounts. when authentication state changes
  // the user state is updates and fetches the list of items and transaction
  // history based on the specific user
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      if (currentUser) {
        setUser(currentUser);
        // fetchListOfItems(currentUser.email);
        // fetchTransactionHistory(currentUser.email);
      } else {
        router.push("/");
      }
    });

    // Cleanup subscription on unmount
    return () => unsubscribe();
  }, [router]);

  // logs the user out by using the firebase's signOut method
  const logOut = async () => {
    try {
      await signOut(auth);
      router.push("/");
    } catch (err) {
      console.error(err);
    }
  };

  const signInWithGoogle = async () => {
    try {
      await signInWithPopup(auth, googleProvider);
    } catch (err) {
      console.error(err);
    }
  };

  const uploadContactInformation = async () => {
    if (!location) {
      setLocationFilled(false);
      alert("Location is required");
      return;
    } else {
      setLocationFilled(true);
    }

    setShowUploadUserInfoButton(true);
    setShowLocationTooltip(true);
    setShowPhoneNumberTooltip(true);

    try {
      // Then, create a document in Firestore with the item data
<<<<<<< HEAD
      console.log(user.uid);
      const userData = {
        userID: user.uid,
        phoneNumber: phoneNumber,
        location: location,
      };

      const response = await fetch("api/profile/upload_contact_info", {
=======
      const userData = {
        phoneNumber: phoneNumber,
        location: location,
        type: "request",
      };

      const response = await fetch("api/profile/update_contact_info", {
>>>>>>> 113ee4eb2eeac41b0e6866367de36b574e58e64e
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
<<<<<<< HEAD
        body: JSON.stringify(userData),
=======
        body: JSON.stringify(requestData),
>>>>>>> 113ee4eb2eeac41b0e6866367de36b574e58e64e
      });

      const data = await response.json();
      if (response.ok) {
        alert("Request uploaded successfully!");
        // Clear the form
<<<<<<< HEAD
        setPhoneNumber("");
        setLocation("");
=======
        setPhoneNumber();
        setLocation();
>>>>>>> 113ee4eb2eeac41b0e6866367de36b574e58e64e
      } else {
        alert("Failed to upload request: " + data.message);
      }
    } catch (error) {
      console.error("Failed to fetch:", error);
      alert("An error occurred. Please try again.");
    }
  };

  const handleChangeUserInfo = () => {
    // Hide the "Upload user info" button and tooltips
    setShowUploadUserInfoButton(false);
    setShowLocationTooltip(false);
    setShowPhoneNumberTooltip(false);
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
    zIndex: "10",
    marginTop: "5px",
  };

  const fetchListOfItems = async () => {
    try {
      setLoading(true);
      console.log("hi");
      const response = await fetch(
        `/api/profile/get_list_of_items?requester_id=${user.uid}`
      );
      if (!response.ok) {
        console.log(response);
        throw new Error("Failed to fetch list of items");
      }
      const data = await response.json();
      console.log(data);
<<<<<<< HEAD
      setItems(data.listingOfItems);
=======
      setItems(response.data.listingOfItems);
>>>>>>> 113ee4eb2eeac41b0e6866367de36b574e58e64e
    } catch (err) {
      console.error(err);
      setError("Failed to fetch list of items");
    } finally {
      setLoading(false);
    }
  };

  const fetchTransactionHistory = async (email) => {
    try {
      setLoading(true);
      console.log("hi");
      const response = await fetch(
        `/api/profile/get_transaction_history?requester_id=${user.uid}`
      );
      if (!response.ok) {
        console.log(response);
        throw new Error("Failed to fetch transaction history");
      }
      const data = await response.json();
      console.log(data);
      setListings(data.transactionHistory);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch transaction history");
    } finally {
      setLoading(false);
    }
  };

<<<<<<< HEAD
=======
  // updates the user's profile data by taking new profile data as input
  // and then uses updateProfile from firebase to update a user's profile
  const updateUserProfile = async (newProfileData) => {
    try {
      // Update user profile data
      await auth.currentUser.updateProfile(newProfileData);
      // Update the user state with the new profile data
      setUser({ ...user, ...newProfileData });
    } catch (err) {
      console.error(err);
      setError("Failed to update profile");
    }
  };

>>>>>>> 113ee4eb2eeac41b0e6866367de36b574e58e64e
  return (
    <>
      <div>
        {user && (
          <>
            <div
              style={{
                textAlign: "center",
                margin: "30px 0",
              }}
            >
              <h1>Welcome, {user.displayName}</h1>
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
<<<<<<< HEAD
              {uploadInfoButton && !showItemModal && (
                <div style={{ textAlign: "center" }}>
                  <p style={{ marginBottom: "30px" }}>
                    Phone Number: {phoneNumber}
                  </p>
                  <p style={{ marginBottom: "30px" }}>Location: {location}</p>
                  <button
                    className="button is-primary"
                    onClick={handleChangeUserInfo}
                    style={{
                      padding: "15px 20px", // Increased padding for the button
                      fontSize: "16px",
                      color: "white",
                      border: "none",
                      borderRadius: "2px",
                      cursor: "pointer",
                    }}
                  >
                    Change user info
                  </button>
                </div>
              )}
=======
>>>>>>> 113ee4eb2eeac41b0e6866367de36b574e58e64e
              {["phoneNumber", "location", "image"].map((field) => (
                <div
                  key={field}
                  style={{
                    position: "relative",
                    display: "flex",
                    alignItems: "center",
                    gap: "5px",
                  }}
                >
                  {!uploadInfoButton && field === "phoneNumber" && (
                    <input
                      type="number"
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value)}
                      placeholder="Phone Number"
                      style={{
                        padding: "10px",
                        fontSize: "16px",
                        border: "1px solid #ccc",
                        borderRadius: "4px",
                        flexGrow: 1,
                      }}
                    />
                  )}
                  {!uploadInfoButton && field === "location" && (
                    <input
                      type="text"
                      value={location}
                      onChange={(e) => setLocation(e.target.value)}
                      placeholder="Location (Required)"
                      style={{
                        padding: "10px",
                        fontSize: "16px",
                        border: "1px solid #ccc",
                        borderRadius: "4px",
                        flexGrow: 1,
                      }}
                    />
                  )}

                  <button
                    onClick={() => {
                      setShowPhoneNumberTooltip(
                        field === "phoneNumber"
                          ? !showPhoneNumberTooltip
                          : false
                      );
                      setShowLocationTooltip(
                        field === "location" ? !showLocationTooltip : false
                      );
                    }}
                    style={{ position: "relative", zIndex: "20" }}
                  ></button>
                </div>
              ))}
              {!locationFilled && !uploadInfoButton && (
                <button
                  className="button is-primary"
                  onClick={uploadContactInformation}
                  style={{
                    padding: "10px 20px",
                    fontSize: "16px",
                    color: "white",
                    border: "none",
                    borderRadius: "2px",
                    cursor: "pointer",
                  }}
                >
<<<<<<< HEAD
                  Upload user info
                </button>
              )}
=======
                  Update user info
                </button>
              )}
              {uploadInfoButton && (
                <div style={{ textAlign: "center" }}>
                  <p>Phone Number: {phoneNumber}</p>
                  <p>Location: {location}</p>
                  <button
                    className="button is-primary"
                    onClick={() => {
                      locationFilled, uploadInfoButton;
                    }}
                    style={{
                      padding: "10px 20px",
                      fontSize: "16px",
                      color: "white",
                      border: "none",
                      borderRadius: "2px",
                      cursor: "pointer",
                    }}
                  >
                    Change user info
                  </button>
                </div>
              )}
>>>>>>> 113ee4eb2eeac41b0e6866367de36b574e58e64e
            </div>
          </>
        )}
      </div>

      <div>
        {user && (
          <>
            <div
              style={{
                textAlign: "center",
                margin: "30px 0",
              }}
            >
              <h1>Get user information</h1>
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
              <div style={{ display: "flex", gap: "20px" }}>
                <button
                  className="button is-primary"
                  onClick={() => {
<<<<<<< HEAD
                    fetchTransactionHistory();
                    setShowTransactionModal(true);
=======
                    fetchListOfItems;
                    setShowItemModal(true);
>>>>>>> 113ee4eb2eeac41b0e6866367de36b574e58e64e
                  }}
                  style={{
                    padding: "10px 20px",
                    fontSize: "16px",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                  }}
                >
                  Get transaction history
                </button>

                <button
                  className="button is-primary"
                  onClick={() => {
                    fetchListOfItems();
                    setShowItemModal(true);
                  }}
                  //onClick={fetchListOfItems, setShowItemModal(true)}
                  style={{
                    padding: "10px 20px",
                    fontSize: "16px",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                    flex: "1",
                  }}
                >
                  Get list of items
                </button>
              </div>
<<<<<<< HEAD
                  
=======

>>>>>>> 113ee4eb2eeac41b0e6866367de36b574e58e64e
              {showItemModal && (
                <div className="modal is-active">
                  <div
                    className="modal-background"
                    onClick={() => setShowItemModal(false)}
                  ></div>
<<<<<<< HEAD
                  <div
                    className="modal-card"
                    style={{ width: "90%", margin: "auto" }}
                  >
                    <section
                      className="modal-card-body"
                      style={{ maxHeight: "60vh", overflowY: "auto" }}
                    >
                      <div className="card is-shadowless">
                        <div className="card-content px-4 py-">
                          <h2 className="is-size-5">List of Items</h2>
                          {items.length > 0 ? (
                            items.map((item, index) => (
                              <div key={index}>
                                <p>{item.title}</p>
                                <p>{item.description}</p>
                                {/* Add more details as needed */}
                              </div>
                            ))
                          ) : (
                            <p>No items to display</p>
                          )}
=======
                  <div className="modal-card">
                    <section className="modal-card-body">
                      <div className="card is-shadowless">
                        <div className="card-content px-4 py-">
                          <div className="media mb-2 flex items-center"></div>
>>>>>>> 113ee4eb2eeac41b0e6866367de36b574e58e64e
                        </div>
                      </div>
                    </section>
                    <footer className="modal-card-foot">
                      <button className="button is-success">Delete item</button>
                      <button
                        className="button"
                        onClick={() => setShowItemModal(false)}
                      >
                        Close
                      </button>
                    </footer>
                  </div>
                </div>
              )}

<<<<<<< HEAD
              {showTransactionModal && (
                <div className="modal is-active">
                  <div
                    className="modal-background"
                    onClick={() => setShowTransactionModal(false)}
                  ></div>
                  <div
                    className="modal-card"
                    style={{ width: "90%", margin: "auto" }}
                  >
                    <section className="modal-card-body">
                      <div className="card is-shadowless">
                        <div className="card-content px-4 py-">
                          <h2 className="is-size-5">Transaction History</h2>
                          {listings.length > 0 ? (
                            listings.map((listing, index) => (
                              <div key={index}>
                                <p>{listing.name}</p>
                                <p>{listing.description}</p>
                                {/* Add more details as needed */}
                              </div>
                            ))
                          ) : (
                            <p>No listings to display</p>
                          )}
                        </div>
                      </div>
                    </section>
                    <footer className="modal-card-foot">
                      <button className="button is-success">Delete item</button>
                      <button
                        className="button"
                        onClick={() => setShowTransactionModal(false)}
                      >
                        Close
                      </button>
                    </footer>
                  </div>
                </div>
              )}

=======
              {/* {imagePreviewUrl && <img src={imagePreviewUrl} alt="Preview" style={{ maxWidth: '100%', marginTop: '20px' }} />} */}
>>>>>>> 113ee4eb2eeac41b0e6866367de36b574e58e64e
            </div>
          </>
        )}
      </div>
    </>
  );
}
