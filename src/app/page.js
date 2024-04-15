"use client";
import { auth, googleProvider } from "./firebase/config";
import { signInWithPopup, signOut, onAuthStateChanged } from "firebase/auth";
import { ref, uploadBytes } from "firebase/storage";
import { useState, useEffect } from "react";
import { storage } from "./firebase/config";
import { v4 } from "uuid";
import { ItemCard } from "./components/itemCard";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSearch } from "@fortawesome/free-solid-svg-icons";

export default function Home() {
  const [user, setUser] = useState(null);
  const imagesRef = ref(storage, "images");
  const [imageUpload, setImageUpload] = useState(null);
  const [search, setSearch] = useState("");
  const [marketSelected, setMarketSelected] = useState(true);
  const [rentalsSelected, setRentalsSelected] = useState(true);
  const [requestsSelected, setRequestsSelected] = useState(true);

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

  const searchItems = async (e) => {
    e.preventDefault();
    console.log(search);
    // const res = await fetch(`/api/search?query=${search}`);
    // const data = await res.json();
    // console.log(data);
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
      description:
        "Upgrade your kitchen with the Chef's Choice 900W Digital Microwave Oven, the perfect blend of style, efficiency, and convenience. This sleek stainless steel microwave is designed to meet all your cooking needs with ease and precision.",
      category: categories[Math.floor(Math.random() * categories.length)], // Random category
      price: 25, // Random price
      images: ["/images/microwave.jpg"], // Random image URL
      status: statuses[Math.floor(Math.random() * statuses.length)], // Random status
      timestamp: new Date().toISOString(), // Current timestamp
      timeSinceListing: "3h",
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
            <form className="flex justify-center mt-2" onSubmit={searchItems}>
              <div className="field w-full mx-5">
                <div className="control is-expanded flex flex-row">
                  <input
                    className="input"
                    type="text"
                    placeholder="I'm looking for..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                  <button type="submit" className="button is-dark">
                    <FontAwesomeIcon icon={faSearch} />
                  </button>
                </div>
              </div>
            </form>
            <div className="columns is-centered is-mobile mx-1 mt-1 mb-0">
              <div className="column is-one-third has-text-centered">
                <button
                  className={`w-full text-white py-2 px-4 rounded ${
                    marketSelected ? "bg-blue-500" : "bg-blue-300"
                  }`}
                  onClick={() => setMarketSelected(!marketSelected)}
                >
                  Market
                </button>
              </div>
              <div className="column is-one-third has-text-centered">
                <button
                  className={`w-full text-white py-2 px-4 rounded ${
                    rentalsSelected ? "bg-green-500" : "bg-green-300"
                  }`}
                  onClick={() => setRentalsSelected(!rentalsSelected)}
                >
                  Rentals
                </button>
              </div>
              <div className="column is-one-third has-text-centered">
                <button
                  className={`w-full text-white py-2 px-4 rounded ${
                    requestsSelected ? "bg-purple-500" : "bg-purple-300"
                  }`}
                  onClick={() => setRequestsSelected(!requestsSelected)}
                >
                  Requests
                </button>
              </div>
            </div>
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
