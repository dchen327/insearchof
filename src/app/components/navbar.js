"use client";

import { auth, googleProvider } from "../firebase/config";
import { signInWithPopup, signOut, onAuthStateChanged } from "firebase/auth";
import { useState, useEffect } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faList, faShop, faUser } from "@fortawesome/free-solid-svg-icons";
import { faMagnifyingGlass } from "@fortawesome/free-solid-svg-icons";
import Link from "next/link";

export const Navbar = () => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
    });

    // Cleanup subscription on unmount
    return () => unsubscribe();
  }, []);

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

  return (
    <>
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
            <button className="navbar-item" onClick={console.log("hi")}>
              console log
            </button>
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
    </>
  );
};
