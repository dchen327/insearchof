"use client";
import "bulma/css/bulma.css";
import { auth, googleProvider } from "./firebase/config";
import { signInWithPopup, signOut } from "firebase/auth";

export default function Home() {
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

  return (
    <nav className="navbar" role="navigation" aria-label="main navigation">
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
        </div>
        <div className="navbar-end">
          <div className="navbar-item">
            <div className="buttons">
              <button className="button is-primary" onClick={signInWithGoogle}>
                <strong>Sign In</strong>
              </button>
              <button className="button is-light" onClick={logOut}>
                Log out
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
