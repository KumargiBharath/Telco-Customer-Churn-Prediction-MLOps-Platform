// app/components/Dashboard.tsx
"use client";
import React, { useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  Loader2,
  User,
  CreditCard,
  Wifi,
  FileText,
  LogOut,
  Moon,
  Sun,
  Upload,
  History,
  Trash2,
  BarChart3,
  PieChart as PieChartIcon,
  ShieldAlert,
} from "lucide-react";
import { useApp } from "../context/AppContext";
import Papa from "papaparse"; // CSV Parser
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts"; // Charts

// --- Types ---
interface CustomerData {
  gender: string;
  SeniorCitizen: string | number;
  Partner: string;
  Dependents: string;
  tenure: number;
  PhoneService: string;
  MultipleLines: string;
  InternetService: string;
  OnlineSecurity: string;
  OnlineBackup: string;
  DeviceProtection: string;
  TechSupport: string;
  StreamingTV: string;
  StreamingMovies: string;
  Contract: string;
  PaperlessBilling: string;
  PaymentMethod: string;
  MonthlyCharges: number;
  TotalCharges: number;
}

interface PredictionResponse {
  prediction: number;
  prediction_label: string;
  churn_probability: number;
}

interface HistoryItem extends PredictionResponse {
  id: number;
  timestamp: string;
  gender: string;
  contract: string;
  tenure: number;
}

// --- Helper Components ---
const SelectInput = ({ label, name, value, onChange, options }: any) => (
  <div className="flex flex-col space-y-1">
    <label className="text-xs font-medium text-gray-600 dark:text-gray-300">
      {label}
    </label>
    <select
      name={name}
      value={value}
      onChange={onChange}
      className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 text-sm bg-white dark:bg-gray-700 dark:border-gray-600 text-gray-900 dark:text-white"
    >
      {options.map((opt: string) => (
        <option key={opt} value={opt}>
          {opt}
        </option>
      ))}
    </select>
  </div>
);

const NumberInput = ({ label, name, value, onChange, step = 1 }: any) => (
  <div className="flex flex-col space-y-1">
    <label className="text-xs font-medium text-gray-600 dark:text-gray-300">
      {label}
    </label>
    <input
      type="number"
      name={name}
      value={value}
      onChange={onChange}
      step={step}
      className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 text-sm dark:bg-gray-700 dark:border-gray-600 text-gray-900 dark:text-white"
    />
  </div>
);

// --- Dashboard ---
export default function Dashboard() {
  const { logout, theme, toggleTheme } = useApp();

  // State
  const [activeTab, setActiveTab] = useState<"single" | "batch">("single");
  const [formData, setFormData] = useState<CustomerData>({
    gender: "Female",
    SeniorCitizen: "0",
    Partner: "Yes",
    Dependents: "No",
    tenure: 1,
    PhoneService: "No",
    MultipleLines: "No phone service",
    InternetService: "DSL",
    OnlineSecurity: "No",
    OnlineBackup: "Yes",
    DeviceProtection: "No",
    TechSupport: "No",
    StreamingTV: "No",
    StreamingMovies: "No",
    Contract: "Month-to-month",
    PaperlessBilling: "Yes",
    PaymentMethod: "Electronic check",
    MonthlyCharges: 29.85,
    TotalCharges: 29.85,
  });
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [batchData, setBatchData] = useState<any[]>([]); // For CSV results

  const API_URL = "http://localhost:8000/predict";

  // Handlers
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "number" ? parseFloat(value) : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    const payload = {
      ...formData,
      SeniorCitizen: Number(formData.SeniorCitizen),
    };

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error("Failed");
      const data = await response.json();
      setResult(data);
      addToHistory(data, formData);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const addToHistory = (data: PredictionResponse, input: CustomerData) => {
    const newItem: HistoryItem = {
      ...data,
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString(),
      gender: input.gender,
      contract: input.Contract,
      tenure: input.tenure,
    };
    setHistory((prev) => [newItem, ...prev]);
  };

  // CSV Handling
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: async function (results) {
        const rows = results.data as CustomerData[];
        setLoading(true);
        try {
          // Send all rows to backend sequentially (simple approach)
          const promises = rows.map((row) =>
            fetch(API_URL, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                ...row,
                SeniorCitizen: Number(row.SeniorCitizen),
              }),
            }).then((res) => res.json()),
          );

          const results = await Promise.all(promises);

          // Merge input data with results for display
          const combined = results.map((res, i) => ({
            ...res,
            ...rows[i],
          }));

          setBatchData(combined);
          // Add to history
          combined.forEach((item, i) => addToHistory(item, rows[i]));
        } catch (err) {
          setError("Batch processing failed");
        } finally {
          setLoading(false);
        }
      },
    });
  };

  // Explainability Logic
  const getRiskFactors = (data: CustomerData) => {
    const factors = [];
    if (data.Contract === "Month-to-month")
      factors.push("Month-to-month contracts have higher churn rates.");
    if (data.tenure < 12)
      factors.push("Tenure less than 1 year is a risk factor.");
    if (data.InternetService === "Fiber optic")
      factors.push("Fiber optic service shows higher churn in data.");
    if (data.OnlineSecurity === "No")
      factors.push("Lack of Online Security increases risk.");
    return factors.length > 0 ? factors : ["Customer profile looks stable."];
  };

  // Chart Data
  const pieData = [
    {
      name: "Churn",
      value: history.filter((h) => h.prediction === 1).length,
      color: "#ef4444",
    },
    {
      name: "No Churn",
      value: history.filter((h) => h.prediction === 0).length,
      color: "#22c55e",
    },
  ];

  const barData = history.slice(0, 5).map((h) => ({
    name: h.timestamp,
    prob: Math.round(h.churn_probability * 100),
  }));

  // Options
  const binaryOptions = ["Yes", "No"];
  const internetOptions = ["DSL", "Fiber optic", "No"];
  const contractOptions = ["Month-to-month", "One year", "Two year"];
  const paymentOptions = [
    "Electronic check",
    "Mailed check",
    "Bank transfer (automatic)",
    "Credit card (automatic)",
  ];
  const multilineOptions = ["Yes", "No", "No phone service"];
  const onlineOptions = ["Yes", "No", "No internet service"];

  return (
    <main className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4 transition-colors">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-800 dark:text-white">
              Customer Churn Dashboard
            </h1>
            <p className="text-gray-500 dark:text-gray-400 mt-1">
              AI-Powered Prediction & Analytics
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg bg-white dark:bg-gray-700 shadow text-gray-600 dark:text-yellow-300"
            >
              {theme === "light" ? <Moon size={20} /> : <Sun size={20} />}
            </button>
            <button
              onClick={logout}
              className="flex items-center gap-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30 px-4 py-2 rounded-lg font-medium border border-red-200 dark:border-red-800 text-sm"
            >
              <LogOut size={16} /> Sign Out
            </button>
          </div>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Forms */}
          <div className="lg:col-span-2 space-y-6">
            {/* Tab Selector */}
            <div className="flex gap-2 bg-white dark:bg-gray-800 p-1 rounded-lg w-fit shadow-sm">
              <button
                onClick={() => setActiveTab("single")}
                className={`px-4 py-2 rounded-md text-sm font-medium transition ${activeTab === "single" ? "bg-blue-600 text-white" : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"}`}
              >
                Single Prediction
              </button>
              <button
                onClick={() => setActiveTab("batch")}
                className={`px-4 py-2 rounded-md text-sm font-medium transition ${activeTab === "batch" ? "bg-blue-600 text-white" : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"}`}
              >
                Batch Upload (CSV)
              </button>
            </div>

            {activeTab === "single" ? (
              <div className="bg-white dark:bg-gray-800 shadow-md rounded-xl p-6 border border-gray-100 dark:border-gray-700">
                <form onSubmit={handleSubmit} className="space-y-6">
                  {/* Demographics */}
                  <div className="border-b pb-4 dark:border-gray-700">
                    <div className="flex items-center gap-2 mb-4 text-gray-700 font-semibold dark:text-gray-200">
                      <User size={18} /> Demographics
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <SelectInput
                        label="Gender"
                        name="gender"
                        value={formData.gender}
                        onChange={handleChange}
                        options={["Female", "Male"]}
                      />
                      <SelectInput
                        label="Senior Citizen"
                        name="SeniorCitizen"
                        value={formData.SeniorCitizen}
                        onChange={handleChange}
                        options={["0", "1"]}
                      />
                      <SelectInput
                        label="Partner"
                        name="Partner"
                        value={formData.Partner}
                        onChange={handleChange}
                        options={binaryOptions}
                      />
                      <SelectInput
                        label="Dependents"
                        name="Dependents"
                        value={formData.Dependents}
                        onChange={handleChange}
                        options={binaryOptions}
                      />
                    </div>
                  </div>

                  {/* Services */}
                  <div className="border-b pb-4 dark:border-gray-700">
                    <div className="flex items-center gap-2 mb-4 text-gray-700 font-semibold dark:text-gray-200">
                      <Wifi size={18} /> Services
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <NumberInput
                        label="Tenure"
                        name="tenure"
                        value={formData.tenure}
                        onChange={handleChange}
                      />
                      <SelectInput
                        label="Phone Service"
                        name="PhoneService"
                        value={formData.PhoneService}
                        onChange={handleChange}
                        options={binaryOptions}
                      />
                      <SelectInput
                        label="Multiple Lines"
                        name="MultipleLines"
                        value={formData.MultipleLines}
                        onChange={handleChange}
                        options={multilineOptions}
                      />
                      <SelectInput
                        label="Internet Service"
                        name="InternetService"
                        value={formData.InternetService}
                        onChange={handleChange}
                        options={internetOptions}
                      />
                      <SelectInput
                        label="Online Security"
                        name="OnlineSecurity"
                        value={formData.OnlineSecurity}
                        onChange={handleChange}
                        options={onlineOptions}
                      />
                      <SelectInput
                        label="Online Backup"
                        name="OnlineBackup"
                        value={formData.OnlineBackup}
                        onChange={handleChange}
                        options={onlineOptions}
                      />
                      <SelectInput
                        label="Device Protection"
                        name="DeviceProtection"
                        value={formData.DeviceProtection}
                        onChange={handleChange}
                        options={onlineOptions}
                      />
                      <SelectInput
                        label="Tech Support"
                        name="TechSupport"
                        value={formData.TechSupport}
                        onChange={handleChange}
                        options={onlineOptions}
                      />
                      <SelectInput
                        label="Streaming TV"
                        name="StreamingTV"
                        value={formData.StreamingTV}
                        onChange={handleChange}
                        options={onlineOptions}
                      />
                      <SelectInput
                        label="Streaming Movies"
                        name="StreamingMovies"
                        value={formData.StreamingMovies}
                        onChange={handleChange}
                        options={onlineOptions}
                      />
                    </div>
                  </div>

                  {/* Billing */}
                  <div>
                    <div className="flex items-center gap-2 mb-4 text-gray-700 font-semibold dark:text-gray-200">
                      <CreditCard size={18} /> Billing
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <SelectInput
                        label="Contract"
                        name="Contract"
                        value={formData.Contract}
                        onChange={handleChange}
                        options={contractOptions}
                      />
                      <SelectInput
                        label="Paperless Billing"
                        name="PaperlessBilling"
                        value={formData.PaperlessBilling}
                        onChange={handleChange}
                        options={binaryOptions}
                      />
                      <SelectInput
                        label="Payment Method"
                        name="PaymentMethod"
                        value={formData.PaymentMethod}
                        onChange={handleChange}
                        options={paymentOptions}
                      />
                      <NumberInput
                        label="Monthly Charges"
                        name="MonthlyCharges"
                        value={formData.MonthlyCharges}
                        step={0.01}
                        onChange={handleChange}
                      />
                      <NumberInput
                        label="Total Charges"
                        name="TotalCharges"
                        value={formData.TotalCharges}
                        step={0.01}
                        onChange={handleChange}
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:bg-blue-400"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="animate-spin" size={20} />{" "}
                        Analyzing...
                      </>
                    ) : (
                      "Predict Churn"
                    )}
                  </button>
                </form>
              </div>
            ) : (
              // Batch Upload UI
              <div className="bg-white dark:bg-gray-800 shadow-md rounded-xl p-6 border border-gray-100 dark:border-gray-700">
                <h3 className="text-lg font-bold mb-4 dark:text-white">
                  Upload Customer List (CSV)
                </h3>
                <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-10 text-center hover:border-blue-500 transition cursor-pointer">
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="csvUpload"
                  />
                  <label
                    htmlFor="csvUpload"
                    className="cursor-pointer flex flex-col items-center gap-2 text-gray-500 dark:text-gray-400"
                  >
                    <Upload size={32} />
                    <span>Click to upload CSV</span>
                    <span className="text-xs">
                      (Columns must match form fields)
                    </span>
                  </label>
                </div>

                {batchData.length > 0 && (
                  <div className="mt-6 overflow-x-auto">
                    <h4 className="font-semibold mb-2 dark:text-white">
                      Batch Results ({batchData.length} rows)
                    </h4>
                    <table className="w-full text-xs text-left border-collapse">
                      <thead className="bg-gray-50 dark:bg-gray-700">
                        <tr>
                          <th className="p-2 border dark:border-gray-600">
                            Gender
                          </th>
                          <th className="p-2 border dark:border-gray-600">
                            Contract
                          </th>
                          <th className="p-2 border dark:border-gray-600">
                            Prediction
                          </th>
                          <th className="p-2 border dark:border-gray-600">
                            Probability
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {batchData.map((row, i) => (
                          <tr key={i} className="dark:text-gray-300">
                            <td className="p-2 border dark:border-gray-600">
                              {row.gender}
                            </td>
                            <td className="p-2 border dark:border-gray-600">
                              {row.Contract}
                            </td>
                            <td
                              className={`p-2 border dark:border-gray-600 font-bold ${row.prediction === 1 ? "text-red-500" : "text-green-500"}`}
                            >
                              {row.prediction_label}
                            </td>
                            <td className="p-2 border dark:border-gray-600">
                              {(row.churn_probability * 100).toFixed(1)}%
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {/* Analytics Section */}
            {history.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white dark:bg-gray-800 shadow-md rounded-xl p-6 border border-gray-100 dark:border-gray-700">
                  <div className="flex items-center gap-2 mb-4 text-gray-700 font-semibold dark:text-gray-200">
                    <PieChartIcon size={18} /> Churn Distribution
                  </div>
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={60}
                        fill="#8884d8"
                        label
                      >
                        {pieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Legend />
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="bg-white dark:bg-gray-800 shadow-md rounded-xl p-6 border border-gray-100 dark:border-gray-700">
                  <div className="flex items-center gap-2 mb-4 text-gray-700 font-semibold dark:text-gray-200">
                    <BarChart3 size={18} /> Recent Probabilities
                  </div>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={barData}>
                      <XAxis dataKey="name" stroke="#888" fontSize={10} />
                      <YAxis stroke="#888" fontSize={10} />
                      <Tooltip />
                      <Bar dataKey="prob" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </div>

          {/* Right Sidebar: Result & History */}
          <div className="lg:col-span-1 space-y-6">
            {/* Current Result */}
            <div className="bg-white dark:bg-gray-800 shadow-md rounded-xl p-6 border border-gray-100 dark:border-gray-700">
              <div className="flex items-center gap-2 mb-4 border-b pb-4 text-gray-700 font-semibold dark:text-gray-200">
                <FileText size={18} /> Current Analysis
              </div>
              {error && <div className="text-red-500 text-sm">{error}</div>}

              {result ? (
                <div className="space-y-4">
                  <div
                    className={`p-4 rounded-lg text-center ${result.prediction === 1 ? "bg-red-50 dark:bg-red-900/30" : "bg-green-50 dark:bg-green-900/30"}`}
                  >
                    <h3
                      className={`text-lg font-bold ${result.prediction === 1 ? "text-red-700 dark:text-red-300" : "text-green-700 dark:text-green-300"}`}
                    >
                      {result.prediction_label}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      Probability: {(result.churn_probability * 100).toFixed(1)}
                      %
                    </p>
                  </div>

                  {/* Explainability */}
                  <div className="bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded-lg border border-yellow-100 dark:border-yellow-800">
                    <div className="flex items-center gap-2 text-yellow-800 dark:text-yellow-200 font-medium text-sm mb-2">
                      <ShieldAlert size={14} /> Key Factors
                    </div>
                    <ul className="text-xs text-yellow-700 dark:text-yellow-300 list-disc list-inside space-y-1">
                      {getRiskFactors(formData).map((f, i) => (
                        <li key={i}>{f}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <div className="text-center text-gray-400 py-10">
                  No prediction yet
                </div>
              )}
            </div>

            {/* History */}
            <div className="bg-white dark:bg-gray-800 shadow-md rounded-xl p-6 border border-gray-100 dark:border-gray-700">
              <div className="flex items-center justify-between mb-4 border-b pb-4 text-gray-700 font-semibold dark:text-gray-200">
                <div className="flex items-center gap-2">
                  <History size={18} /> History
                </div>
                {history.length > 0 && (
                  <button
                    onClick={() => setHistory([])}
                    className="text-xs text-gray-400 hover:text-red-500"
                  >
                    <Trash2 size={12} />
                  </button>
                )}
              </div>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {history.length > 0 ? (
                  history.map((item) => (
                    <div
                      key={item.id}
                      className={`p-2 rounded-lg border ${item.prediction === 1 ? "border-red-100 bg-red-50 dark:bg-red-900/20 dark:border-red-800" : "border-green-100 bg-green-50 dark:bg-green-900/20 dark:border-green-800"}`}
                    >
                      <div className="flex justify-between items-center">
                        <span
                          className={`text-xs font-bold ${item.prediction === 1 ? "text-red-700 dark:text-red-300" : "text-green-700 dark:text-green-300"}`}
                        >
                          {item.prediction_label}
                        </span>
                        <span className="text-xs text-gray-400">
                          {item.timestamp}
                        </span>
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {item.gender} / {item.contract}
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-center text-gray-400 text-xs py-4">
                    No history
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
