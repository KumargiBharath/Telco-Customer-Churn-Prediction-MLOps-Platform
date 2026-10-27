// app/page.tsx
"use client";
import { useApp } from "./context/AppContext";
import AuthPage from "./components/AuthPage";
import Dashboard from "./components/Dashboard";

export default function Home() {
  const { user } = useApp();
  return user ? <Dashboard /> : <AuthPage />;
}
