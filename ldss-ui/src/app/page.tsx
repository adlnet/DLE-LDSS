"use client";

import { useRouter } from "next/navigation";
import Footer from "../../components/Footer";
import Head from "next/head";
import Header from "../../components/Header";
import Image from "next/image";
import React, { useState } from "react";

export default function Home() {
  const router = useRouter();
  const [keyword, setKeyword] = useState("");
  const [error, setError] = useState("");

  const handleSearch = () => {
    
    // If nothing entered, do nothing.
    if (!keyword.trim()) return;

    // If too long, set and show error and do nothing.
    if (keyword.length >= 250){
      setError("Search is too long");
      console.error("Search keyword exceeds maximum length of 250 characters.");
      return;
    }
    
    setError("");
    router.push(`/search?keyword=${encodeURIComponent(keyword.trim())}`);
  };

  return (
    <>
      <Head>
        <title>Experience Discovery Service</title>
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <Header />
      <div className="max-w-7xl mx-auto flex flex-col items-center justify-center mt-10">
      <Image
        src="/logo.png"
        alt="Logo"
        width={150}
        height={150}
      />
        <h1 className="text-3xl font-bold mt-4">LDSS</h1>
        <h2 className="text-xl font-sans mt-2">Department of Defense</h2>
      </div>

      <div className="w-[44rem] mx-auto mt-10">
        <div className="border border-gray-300 rounded-lg p-6 bg-gray-100 flex gap-2">
          <input
            type="text"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="Search courses…"
            className="flex-grow px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          <button
            onClick={handleSearch}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Search
          </button>

          {error && error !== "" && (
            <div className="text-red-500 text-sm mt-2">
              {error}
            </div>
          )}
        </div>
      </div>
      <Footer />
    </>
  );
}