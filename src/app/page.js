"use client";
import { auth, googleProvider } from "./firebase/config";
import { signInWithPopup, signOut, onAuthStateChanged } from "firebase/auth";
import { ref, uploadBytes } from "firebase/storage";
import { useState, useEffect } from "react";
import { storage } from "./firebase/config";
import { v4 } from "uuid";
import { ItemCard } from "./components/itemCard";

export default function Home() {
  const [user, setUser] = useState(null);
  const imagesRef = ref(storage, "images");
  const [imageUpload, setImageUpload] = useState(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
    });

    // Cleanup subscription on unmount
    return () => unsubscribe();
  }, []);

  const uploadFile = () => {
    if (imageUpload == null) return;
    const imageRef = ref(storage, `images/${imageUpload.name + v4()}`);
    uploadBytes(imageRef, imageUpload);
  };

  const signInWithGoogle = async () => {
    try {
      await signInWithPopup(auth, googleProvider);
    } catch (err) {
      console.error(err);
    }
  };

  const logOut = async () => {
    try {
      await signOut(auth);
      console.log("signed out");
    } catch (err) {
      console.error(err);
    }
  };

  const testAPI = async () => {
    const res = await fetch("/api/helloworld");
    const data = await res.json();
    console.log(data);
  };

  const uploadImage = async (e) => {
    const file = e.target.files[0];
    const metadata = {
      contentType: "image/jpeg",
    };

    const uploadTask = await imagesRef.put(file, metadata);
    console.log("uploading...");
    uploadTask.on(
      "state_changed",
      (snapshot) => {
        console.log(snapshot);
      },
      (error) => {
        console.error(error);
      },
      () => {
        console.log("uploaded");
      }
    );
  };

  const generateRandomItem = () => {
    const categories = [
      "Electronics",
      "Books",
      "Clothing",
      "Home",
      "Sports",
      "Toys",
    ];
    const statuses = ["Available", "Sold", "Reserved"];

    const item = {
      itemID: Math.floor(Math.random() * 1000000), // Random number for itemId
      sellerUserID: "davidchen@hmc.edu",
      title: "Microwave",
      description: `This is a description for item ${Math.floor(
        Math.random() * 1000
      )}`, // Random description
      category: categories[Math.floor(Math.random() * categories.length)], // Random category
      price: (Math.random() * 100).toFixed(2), // Random price
      images: ["/images/microwave.jpg"], // Random image URL
      status: statuses[Math.floor(Math.random() * statuses.length)], // Random status
      timestamp: new Date().toISOString(), // Current timestamp
    };

    return item;
  };

  const testItem = generateRandomItem();
  const items = [testItem, testItem, testItem];

  return (
    <div>
      <div>
        {user ? (
          <>
            {items.map((item, idx) => (
              <>
                <ItemCard key={idx} item={item} />
                {idx !== items.length - 1 && <hr className="py-[1px]" />}
              </>
            ))}
          </>
        ) : (
          <>
            <p>Please sign in with Google</p>
            <button
              className="button mt-2 is-primary is-hidden-desktop"
              onClick={signInWithGoogle}
            >
              <strong>Sign In</strong>
            </button>
          </>
        )}
      </div>
    </div>
  );
}
