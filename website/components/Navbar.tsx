'use client';
import Link from "next/link";
import { Home } from 'lucide-react';
import { useState } from "react";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="bg-gray-900 text-white shadow-lg fixed w-full z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Left Section - Home Link */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center gap-2 text-xl font-semibold text-white hover:text-gray-300">
              <Home size={20} />
              <span>Home</span>
            </Link>
          </div>

          {/* Right Section - Navigation Links */}
          <div className="hidden md:flex space-x-8">
            <Link href="/chat" className="hover:text-gray-300 transition duration-300">
              Chat Bot
            </Link>
            {/* Uncomment or add other links as needed */}
            {/* <Link href="/analytics" className="hover:text-gray-300 transition duration-300">Analytics</Link> */}
            {/* <Link href="/business" className="hover:text-gray-300 transition duration-300">Business</Link> */}
          </div>

          {/* Mobile Menu Button */}
          <div className="flex md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="text-gray-300 hover:text-white focus:outline-none focus:text-white"
            >
              <svg className="h-6 w-6" stroke="currentColor" fill="none" viewBox="0 0 24 24">
                {isOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {isOpen && (
        <div className="md:hidden bg-gray-800">
          <Link href="/chat" className="block px-4 py-2 text-sm hover:bg-gray-700">
            Chat Bot
          </Link>
          {/* Uncomment or add other links as needed */}
          {/* <Link href="/analytics" className="block px-4 py-2 text-sm hover:bg-gray-700">Analytics</Link> */}
          {/* <Link href="/business" className="block px-4 py-2 text-sm hover:bg-gray-700">Business</Link> */}
        </div>
      )}
    </nav>
  );
};

export default Navbar;
