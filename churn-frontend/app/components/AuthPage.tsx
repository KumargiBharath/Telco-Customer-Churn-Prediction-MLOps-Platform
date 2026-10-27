// app/components/AuthPage.tsx
"use client";
import React, { useState } from "react";
import { useApp } from "../context/AppContext";
import { LogIn, Moon, Sun, UserPlus } from "lucide-react";

export default function AuthPage() {
  const [isLoginMode, setIsLoginMode] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { signup, login, theme, toggleTheme } = useApp();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isLoginMode) login(email, password);
    else {
      const success = signup(email, password);
      if (success) setIsLoginMode(true);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4 transition-colors">
      {/* Theme Toggle */}
      <button
        onClick={toggleTheme}
        className="absolute top-4 right-4 p-2 rounded-full bg-white dark:bg-gray-700 shadow-lg text-gray-700 dark:text-yellow-300"
      >
        {theme === "light" ? <Moon size={20} /> : <Sun size={20} />}
      </button>

      <div className="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-xl w-full max-w-md border border-gray-200 dark:border-gray-700">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 dark:text-white">
            {isLoginMode ? "Welcome Back" : "Create Account"}
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-2">
            {isLoginMode
              ? "Sign in to access the dashboard"
              : "Sign up to get started with predictions"}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Email
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              placeholder="••••••••"
            />
          </div>
          <button
            type="submit"
            className={`w-full py-3 rounded-lg text-white font-semibold flex items-center justify-center gap-2 transition ${
              isLoginMode
                ? "bg-blue-600 hover:bg-blue-700"
                : "bg-green-600 hover:bg-green-700"
            }`}
          >
            {isLoginMode ? <LogIn size={20} /> : <UserPlus size={20} />}
            {isLoginMode ? "Sign In" : "Sign Up"}
          </button>
        </form>
        <div className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
          {isLoginMode ? (
            <p>
              Don't have an account?{" "}
              <button
                onClick={() => setIsLoginMode(false)}
                className="text-blue-600 font-medium hover:underline"
              >
                Sign Up
              </button>
            </p>
          ) : (
            <p>
              Already have an account?{" "}
              <button
                onClick={() => setIsLoginMode(true)}
                className="text-blue-600 font-medium hover:underline"
              >
                Sign In
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
