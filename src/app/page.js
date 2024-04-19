"use client";
import { auth, googleProvider } from "./firebase/config";
import { signInWithPopup, signOut, onAuthStateChanged } from "firebase/auth";
import { ref, uploadBytes } from "firebase/storage";
import { useState, useEffect } from "react";
import { storage } from "./firebase/config";
import { v4 } from "uuid";
import { ItemCard } from "./components/itemCard";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faAngleDown, faSearch } from "@fortawesome/free-solid-svg-icons";
import { useAuthState } from "react-firebase-hooks/auth";

export default function Home() {
  const [user, loading, error] = useAuthState(auth);
  const imagesRef = ref(storage, "images");
  const [imageUpload, setImageUpload] = useState(null);
  const [search, setSearch] = useState("");
  const [showFilterModal, setShowFilterModal] = useState(false);
  const [marketSelected, setMarketSelected] = useState(true);
  const [rentalsSelected, setRentalsSelected] = useState(true);
  const [requestsSelected, setRequestsSelected] = useState(true);

  // filter modal
  const [category, setCategory] = useState("All");
  const [sortBy, setSortBy] = useState("uploadDateAsc");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [showItemModal, setShowItemModal] = useState(false);
  const [currentItem, setCurrentItem] = useState(null);

  // temp variables for filter modal
  const [tempCategory, setTempCategory] = useState(category);
  const [tempSortBy, setTempSortBy] = useState(sortBy);
  const [tempMinPrice, setTempMinPrice] = useState(minPrice);
  const [tempMaxPrice, setTempMaxPrice] = useState(maxPrice);

  const [items, setItems] = useState([]);

  useEffect(() => {
    const fetchItems = async () => {
      const response = await fetch("/api/catalog/listings");
      const data = await response.json();
      setItems(data?.listings || []);
    };

    fetchItems();
  }, []);

  // when the modal is opened, update the temporary variables with the current values
  useEffect(() => {
    if (showFilterModal) {
      setTempCategory(category);
      setTempSortBy(sortBy);
      setTempMinPrice(minPrice);
      setTempMaxPrice(maxPrice);
    }
  }, [category, maxPrice, minPrice, showFilterModal, sortBy]);

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
    const res = await fetch("/api/catalog/test");
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
    const listingTypes = [];
    if (marketSelected) listingTypes.push("buy");
    if (rentalsSelected) listingTypes.push("rent");
    if (requestsSelected) listingTypes.push("request");

    const params = new URLSearchParams();
    params.append("search", search);
    params.append("sort", sortBy);
    params.append("min_price", minPrice || 0);
    params.append("max_price", maxPrice || 0);

    listingTypes.forEach((type) => params.append("listing_types", type));
    params.append("categories", category);

    const response = await fetch(`/api/catalog/listings?${params.toString()}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();
    const listings = data?.listings || [];
    setItems(listings);
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen mx-10">
        <progress
          className="progress is-small is-primary max-w-[500px]"
          max="100"
        ></progress>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p>Error: {error}</p>
      </div>
    );
  }

  if (user) {
    return (
      <div>
        <div>
          <form className="flex justify-center mt-2" onSubmit={searchItems}>
            <div className="field has-addons w-full mx-2">
              <div className="control is-expanded">
                <input
                  className="input"
                  type="text"
                  placeholder="I'm looking for..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>
              <div className="control">
                <button
                  className="button"
                  onClick={() => setShowFilterModal(true)}
                >
                  Filters
                  <FontAwesomeIcon
                    className="ml-1"
                    icon={faAngleDown}
                    size="sm"
                  />
                </button>
              </div>
              <div className="control">
                <button type="submit" className="button is-warning">
                  <FontAwesomeIcon icon={faSearch} />
                </button>
              </div>
            </div>
          </form>
          <div className="columns is-centered is-mobile mx-1 mt-1 mb-0">
            <div className="column is-one-third has-text-centered p-1">
              <button
                className={`w-full text-white py-2 px-2 rounded ${
                  marketSelected ? "bg-blue-500" : "bg-blue-300"
                }`}
                onClick={() => setMarketSelected(!marketSelected)}
              >
                Market
              </button>
            </div>
            <div className="column is-one-third has-text-centered p-1">
              <button
                className={`w-full text-white py-2 px-2 rounded ${
                  rentalsSelected ? "bg-green-500" : "bg-green-300"
                }`}
                onClick={() => setRentalsSelected(!rentalsSelected)}
              >
                Rentals
              </button>
            </div>
            <div className="column is-one-third has-text-centered p-1">
              <button
                className={`w-full text-white py-2 px-2 rounded ${
                  requestsSelected ? "bg-purple-500" : "bg-purple-300"
                }`}
                onClick={() => setRequestsSelected(!requestsSelected)}
              >
                Requests
              </button>
            </div>
          </div>
          {showFilterModal && (
            <div className="modal is-active">
              <div
                className="modal-background"
                onClick={() => setShowFilterModal(false)}
              ></div>
              <div className="modal-card">
                <header className="modal-card-head">
                  <p className="modal-card-title">Filter and Sort</p>
                  <button
                    className="delete"
                    aria-label="close"
                    onClick={() => setShowFilterModal(false)}
                  ></button>
                </header>
                <section className="modal-card-body">
                  <div className="columns is-centered is-mobile">
                    <div className="column field">
                      <label className="label">Category</label>
                      <div className="control is-expanded">
                        <div className="select is-fullwidth">
                          <select
                            value={tempCategory}
                            onChange={(e) => setTempCategory(e.target.value)}
                          >
                            <option value="All">All</option>
                            <option value="Food">Food</option>
                            <option value="electronics">Electronics</option>
                            <option value="furniture">Furniture</option>
                            <option value="clothing">Clothing</option>
                          </select>
                        </div>
                      </div>
                    </div>
                    <div className="column field">
                      <label className="label">Sort By</label>
                      <div className="control is-expanded">
                        <div className="select is-fullwidth">
                          <select
                            value={tempSortBy}
                            onChange={(e) => setTempSortBy(e.target.value)}
                          >
                            <option value="uploadDateAsc">Date (Newest)</option>
                            <option value="uploadDateDesc">
                              Date (Oldest)
                            </option>
                            <option value="priceAsc">
                              Price (Low to High)
                            </option>
                            <option value="priceDesc">
                              Price (High to Low)
                            </option>
                          </select>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="columns is-centered is-mobile">
                    <div className="column field">
                      <label className="label ml-2">Min</label>
                      <div className="field has-addons">
                        <p className="control">
                          <a className="button is-static">$</a>
                        </p>
                        <div className="control">
                          <input
                            className="input"
                            type="number"
                            min="0"
                            value={tempMinPrice}
                            onChange={(e) => setTempMinPrice(e.target.value)}
                          />
                        </div>
                      </div>
                    </div>
                    <div className="column field">
                      <label className="label ml-2">Max</label>
                      <div className="field has-addons">
                        <p className="control">
                          <a className="button is-static">$</a>
                        </p>
                        <div className="control">
                          <input
                            className="input"
                            type="number"
                            min="0"
                            value={tempMaxPrice}
                            onChange={(e) => setTempMaxPrice(e.target.value)}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </section>
                <footer className="modal-card-foot">
                  <button
                    className="button is-success"
                    onClick={() => {
                      setCategory(tempCategory);
                      setSortBy(tempSortBy);
                      setMinPrice(tempMinPrice);
                      setMaxPrice(tempMaxPrice);
                      setShowFilterModal(false);
                    }}
                  >
                    Apply Filters
                  </button>
                  <button
                    className="button"
                    onClick={() => setShowFilterModal(false)}
                  >
                    Cancel
                  </button>
                </footer>
              </div>
            </div>
          )}
          {items.map((item, idx) => (
            <>
              <div
                onClick={() => {
                  setCurrentItem(item);
                  setShowItemModal(true);
                }}
              >
                <ItemCard key={idx} item={item} />
              </div>
              {idx !== items.length - 1 && <hr className="py-[1px]" />}
            </>
          ))}
          {showItemModal && currentItem && (
            <div className="modal is-active">
              <div
                className="modal-background"
                onClick={() => setShowItemModal(false)}
              ></div>
              <div className="modal-card">
                <section className="modal-card-body">
                  <div className="card is-shadowless">
                    <div className="card-content px-4 py-">
                      <div className="media mb-2 flex items-center">
                        <div className="media-content">
                          <p className="title is-4 mb-2">{currentItem.title}</p>
                          <div className="flex flex-row mb-0">
                            <p className="is-6">{currentItem.user_name}</p>
                            <p className="is-6 font-thin">•</p>
                            {/* todo: backend calculations  */}
                            <p className="is-6">
                              {currentItem.time_since_listing}
                            </p>
                          </div>
                        </div>
                        <div className="bg-gray-100 rounded">
                          <p className="p-1 text-lg text-black is-4">
                            ${currentItem.price}
                          </p>
                        </div>
                      </div>
                      <div className="content">{currentItem.description}</div>
                    </div>
                  </div>
                </section>
                <footer className="modal-card-foot">
                  <button className="button is-success">Contact Seller</button>
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
        </div>
      </div>
    );
  }

  return (
    <div className="container m-5 has-text-centered">
      <p>Please sign in with Google</p>
      <button
        className="button mt-2 is-primary is-hidden-desktop"
        onClick={signInWithGoogle}
      >
        <strong>Sign In</strong>
      </button>
    </div>
  );
}
