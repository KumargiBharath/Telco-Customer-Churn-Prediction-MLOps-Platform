// app/context/AppContext.tsx
"use client";
import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

interface User {
  email: string;
}

interface AppContextType {
  user: User | null;
  signup: (email: string, password: string) => boolean;
  login: (email: string, password: string) => boolean;
  logout: () => void;
  theme: "light" | "dark";
  toggleTheme: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [theme, setTheme] = useState<"light" | "dark">("light");

  // Init: Load User and Theme
  useEffect(() => {
    const storedUser = localStorage.getItem("churn_user");
    if (storedUser) setUser(JSON.parse(storedUser));

    const storedTheme = localStorage.getItem("churn_theme") as
      | "light"
      | "dark"
      | null;
    if (storedTheme) {
      setTheme(storedTheme);
      if (storedTheme === "dark")
        document.documentElement.classList.add("dark");
    }

    setLoading(false);
  }, []);

  const signup = (email: string, password: string): boolean => {
    const existingUsers = JSON.parse(
      localStorage.getItem("churn_users_db") || "[]",
    );
    if (existingUsers.find((u: any) => u.email === email)) {
      alert("User already exists! Please Sign In.");
      return false;
    }
    existingUsers.push({ email, password });
    localStorage.setItem("churn_users_db", JSON.stringify(existingUsers));
    alert("Account created successfully! Please Sign In.");
    return true;
  };

  const login = (email: string, password: string): boolean => {
    const existingUsers = JSON.parse(
      localStorage.getItem("churn_users_db") || "[]",
    );
    const foundUser = existingUsers.find(
      (u: any) => u.email === email && u.password === password,
    );
    if (foundUser) {
      const userData = { email: foundUser.email };
      setUser(userData);
      localStorage.setItem("churn_user", JSON.stringify(userData));
      return true;
    }
    alert("Invalid email or password.");
    return false;
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("churn_user");
  };

  const toggleTheme = () => {
    setTheme((prev) => {
      const next = prev === "light" ? "dark" : "light";
      localStorage.setItem("churn_theme", next);
      if (next === "dark") document.documentElement.classList.add("dark");
      else document.documentElement.classList.remove("dark");
      return next;
    });
  };

  return (
    <AppContext.Provider
      value={{ user, signup, login, logout, theme, toggleTheme }}
    >
      {!loading && children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) throw new Error("useApp must be used within an AppProvider");
  return context;
};
