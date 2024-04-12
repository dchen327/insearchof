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
  }, []);

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
      <div className="buttons">
        <button className="button is-light" onClick={logOut}>
          Log out
        </button>
      </div>
    </>
  );
}
