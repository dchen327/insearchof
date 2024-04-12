"use client";
import { auth } from "../firebase/config";
import { useEffect, useState } from "react";
import { signOut, onAuthStateChanged } from "firebase/auth";
import { useRouter } from "next/navigation";

export default function Page() {
  const [user, setUser] = useState(null);
  const router = useRouter();

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

  const logOut = async () => {
    try {
      await signOut(auth);
      console.log("signed out");
    } catch (err) {
      console.error(err);
    }
  };

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

  const handleProfileUpdate = (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const newProfileData = {
      name: formData.get("name"),
      email: formData.get('email'),
      phone_number: formData.get("phone_number"),
      location: formData.get("location"),
    };
    updateUserProfile(newProfileData);
  };

  return (
    <>
      <div className="buttons">
                {user ? (
                  <button className="button is-light" onClick={logOut}>
                    Log out
                  </button>
                ) : (
                  <button
                    className="button is-primary"
                    onClick={signInWithGoogle}
                  >
                    <strong>Sign In</strong>
                  </button>
                )}
              </div>

      <div>
      {user && (
      <div>
        <p>Welcome, {user.name}</p>
        <p>Email: {user.email}</p>
        <p>Phone number, {user.phone_number}</p>
        <p>Location, {user.location}</p>
        {/* Display profile picture if available */}
        {user.photoURL && <img src={user.photoURL} alt="Profile" />}
      </div>
      )}

      <div>
        <ul>
          <li><a href="/dashboard">Dashboard</a></li>
          <li><a href="/settings">Settings</a></li>
          {/* Add more navigation links as needed */}
        </ul>
      </div>
      {user && (
            <div>
              <form onSubmit={handleProfileUpdate}>
                <label>
                  Name:
                  <input 
                    type="text" 
                    name="name" 
                    defaultValue={user.name} />
                </label>
                <br />
                <label>
                  Email:
                  <input 
                    type="text" 
                    name="email" 
                    defaultValue={user.email} />
                </label>
                <br />
                <label>
                  Phone Number:
                  <input
                    type="text"
                    name="phone_number"
                    defaultValue={user.phone_number}
                  />
                </label>
                <br />
                <label>
                  Location:
                  <input
                    type="text"
                    name="location"
                    defaultValue={user.location}
                  />
                </label>
                <br />
                <button type="submit">Update Profile</button>
              </form>
              {error && <p>{error}</p>}
            </div>
          )}

      </div>
    </>
  );
              
}
