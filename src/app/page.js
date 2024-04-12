"use client";
import "bulma/css/bulma.css";
import { auth, googleProvider } from "./firebase/config";
import { signInWithPopup, signOut, onAuthStateChanged } from "firebase/auth";
import { ref, uploadBytes } from "firebase/storage";
import { useState, useEffect } from "react";
import { storage } from "./firebase/config";
import { v4 } from "uuid";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faList,
  faRepeat,
  faShop,
  faUser,
} from "@fortawesome/free-solid-svg-icons";
import { faMagnifyingGlass } from "@fortawesome/free-solid-svg-icons";
import Link from "next/link";

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

  return (
    <div>
      <nav
        className="navbar is-hidden-mobile"
        role="navigation"
        aria-label="main navigation"
      >
        <div className="navbar-brand">
          <a className="navbar-item" href="https://bulma.io">
            <img
              src="https://bulma.io/images/bulma-logo.png"
              width={112}
              height={28}
              alt="logo"
            />
          </a>
          <button
            className="navbar-burger"
            aria-label="menu"
            aria-expanded="false"
            data-target="navbarBasicExample"
          >
            <span aria-hidden="true" />
            <span aria-hidden="true" />
            <span aria-hidden="true" />
          </button>
        </div>
        <div id="navbarBasicExample" className="navbar-menu">
          <div className="navbar-start">
            {/* add button or a tag that when clicked calls /api/helloworld */}
            <button className="navbar-item" onClick={testAPI}>
              test api
            </button>
            {/* upload file */}
            <div className="navbar-item">
              <input
                type="file"
                onChange={(event) => {
                  setImageUpload(event.target.files[0]);
                }}
              />
              <button className="button is-primary" onClick={uploadFile}>
                {" "}
                Upload Image
              </button>
            </div>
          </div>
          <div className="navbar-end">
            <div className="navbar-item">
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
            </div>
          </div>
        </div>
      </nav>
      <nav
        className="navbar is-fixed-bottom is-hidden-tablet"
        role="navigation"
      >
        <hr className="my-1" />
        <div className="navbar-brand">
          <Link
            href="/"
            className="navbar-item is-expanded is-block has-text-centered"
          >
            <FontAwesomeIcon icon={faShop} />
            <p className="is-size-7">Market</p>
          </Link>
          <Link
            href="/listings"
            className="navbar-item is-expanded is-block has-text-centered"
          >
            <FontAwesomeIcon icon={faList} />
            <p className="is-size-7">Listings</p>
          </Link>
          <Link
            href="/insearchof"
            className="navbar-item is-expanded is-block has-text-centered"
          >
            <FontAwesomeIcon icon={faMagnifyingGlass} />
            <p className="is-size-7">ISO</p>
          </Link>
          <Link
            href="/profile"
            className="navbar-item is-expanded is-block has-text-centered"
          >
            <FontAwesomeIcon icon={faUser} />
            <p className="is-size-7">Profile</p>
          </Link>
        </div>
      </nav>
      <div className="box">
        {user ? (
          <p>Welcome {user.displayName}</p>
        ) : (
          <p>Please sign in with Google</p>
        )}
      </div>
    </div>
  );
}
