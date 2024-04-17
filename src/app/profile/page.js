
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
  const [transactionHistory, setTransactionHistory] = useState([]);
  const [showNameTooltip, setShowNameTooltip] = useState(false); // Added state variables for tooltips
  const [showPhoneNumberTooltip, setShowPhoneNumberTooltip] = useState(false);
  const [showLocationTooltip, setShowLocationTooltip] = useState(false);
  const [name, setName] = useState(""); // Added state variables for name, email, phoneNumber, and location
  const [phoneNumber, setPhoneNumber] = useState("");
  const [location, setLocation] = useState("");
  const router = useRouter();

  // performs side effects in function components. subscribes authentication
  // state changes when the component mounts. when authentication state changes
  // the user state is updates and fetches the list of items and transaction
  // history based on the specific user
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      if (currentUser) {
        setUser(currentUser);
        fetchListOfItems(currentUser.email);
        fetchTransactionHistory(currentUser.email);
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
    if (!name) {
      alert("Name is required");
      return;
    }

    if (!email) {
      alert("Email is required");
      return;
    }

    if (!location) {
      alert("Location is required");
      return;
    }

    // Then, create a document in Firestore with the item data
    const userData = {
      name,
      email,
      phoneNumber,
      location,
      timestamp: new Date(), // You can use Firebase server timestamps as well
    };

    try {
      await addDoc(itemsCollectionRef, userData);
      alert("Request uploaded successfully!");

      // Clear the form
      setName("");
      setPhoneNumber("");
      setLocation(null);
    } catch (error) {
      console.error("Error uploading contact information:", error);
      alert("Failed to upload contact inforation: " + error.message);
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
    zIndex: "10",
    marginTop: "5px",
  };

  const fetchListOfItems = async (email) => {
    try {
      setLoading(true);
      const response = await fetch(
        "/profile/get_list_of_items?requester_id=${email}"
      );
      if (!response.ok) {
        throw new Error("Failed to fetch list of items");
      }
      setItems(response.data.listingOfItems);
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
      const response = await fetch(
        "/profile/get_transaction_history?requester_id=${email}"
      );
      if (!response.ok) {
        throw new Error("Failed to fetch transaction history");
      }
      const data = await response.json();
      setTransactionHistory(data.listingOfTransactionHistory);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch transaction history");
    } finally {
      setLoading(false);
    }
  };

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

  const handleProfileUpdate = async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const newProfileData = {
      name: formData.get("name"),
      email: formData.get("email"),
      phone_number: formData.get("phone_number"),
      location: formData.get("location"),
    };
    updateUserProfile(newProfileData);
  };

  return (
    <>
      <div>
        {user && (
          <>
            <div style={{
              textAlign: 'center',
              margin: '30px 0',
            }}>
              <h1>Welcome, {user.email}</h1>
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
              {['name', 'phoneNumber', 'location', 'image'].map((field) => (
                <div key={field} style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: '5px' }}>
                  {field === "name" && (
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="Name (Required)"
                      style={{
                        padding: "10px",
                        fontSize: "16px",
                        border: "1px solid #ccc",
                        borderRadius: "4px",
                        flexGrow: 1,
                      }}
                    />
                  )}
                  {field === "phoneNumber" && (
                    <input
                      type="text"
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
                  {field === "location" && (
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
                  {/* {field === 'image' && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                      <label style={{ flexGrow: 1, display: 'flex', alignItems: 'center' }}>
                        <span style={{ marginRight: '10px', fontSize: '16px' }}>Image (optional)</span>
                        <input
                          type="file"
                          //onChange={handleImageChange}
                          accept="image/*"
                          style={{ padding: '10px', fontSize: '16px', border: '1px solid #ccc', borderRadius: '4px', flexGrow: 1 }}
                        />
                      </label>
                    </div>
                  )} */}
                  <button
                    onClick={() => {
                      setShowNameTooltip(
                        field === "name" ? !showNameTooltip : false
                      );
                      setShowPhoneNumberTooltip(
                        field === "phoneNumber" ? !showPhoneNumberTooltip : false
                      );
                      setShowLocationTooltip(
                        field === "location" ? !showLocationTooltip : false
                      );
                    }}
                    style={{ position: 'relative', zIndex: '20' }}
                  >
                  </button>
                  {showNameTooltip && field === "name" && (
                    <div style={tooltipStyle}>The user's name</div>
                  )}
                  {showPhoneNumberTooltip && field === "phoneNumber" && (
                    <div style={tooltipStyle}>The phone number of the user</div>
                  )}
                  {showLocationTooltip && field === "location" && (
                    <div style={tooltipStyle}>
                      The location of the user for picking up requested item
                    </div>
                  )}
                </div>
              ))}
              <button className="button is-primary" onClick={updateUserProfile} style={{
                padding: '10px 20px',
                fontSize: '16px',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}>
                Update user info
              </button>
              <button
                className="button is-primary"
                //onClick={() => console.log("Get users transaction history button clicked")}
                style={{ }}
              >
              Get transaction history
              </button>
        
              <button
                className="button is-primary"
                //onClick={() => console.log("Get users list of items button clicked")}
                style={{ }}
              >
              Get list of items
              </button>   
  
              {/* {imagePreviewUrl && <img src={imagePreviewUrl} alt="Preview" style={{ maxWidth: '100%', marginTop: '20px' }} />} */}
            </div>
          </>
        )}
      </div>
  
    </>
  );
}  

