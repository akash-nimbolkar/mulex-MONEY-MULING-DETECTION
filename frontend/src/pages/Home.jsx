import React, { useRef, useState } from "react";
import Papa from "papaparse";
import { Upload, FlaskConical, Download, ArrowRight, Zap, Shield, Loader } from "lucide-react";
import { uploadCSV, runAnalysis, getResults } from "../utils/api";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function onFile(file) {
    setLoading(true);
    setError(null);
    
    try {
      // Step 0: Parse CSV to get transaction rows
      const csvText = await file.text();
      const parseResult = Papa.parse(csvText, { header: true, skipEmptyLines: true });
      const transactionRows = parseResult.data.filter(row => Object.values(row).some(v => v)); // Remove empty rows
      
      if (transactionRows.length === 0) {
        setError("CSV file is empty or invalid");
        setLoading(false);
        return;
      }

      // Step 1: Upload CSV to backend
      const uploadResult = await uploadCSV(file);
      if (!uploadResult.success) {
        setError(`Upload failed: ${uploadResult.error}`);
        setLoading(false);
        return;
      }

      // Step 2: Run analysis on backend
      const analysisResult = await runAnalysis();
      if (!analysisResult.success) {
        setError(`Analysis failed: ${analysisResult.error}`);
        setLoading(false);
        return;
      }

      // Step 3: Get results from backend
      const resultsData = await getResults();
      if (!resultsData.success) {
        setError(`Failed to fetch results: ${resultsData.error}`);
        setLoading(false);
        return;
      }

      // Avoid storing large analysis payload in localStorage (causes quota errors)
      // Store only a small summary and a flag indicating results are ready.
      // Full data will be fetched from the backend when the Analysis page loads.
      localStorage.setItem("analysis_ready", "true");
      if (resultsData.data?.summary) {
        localStorage.setItem("analysis_summary", JSON.stringify(resultsData.data.summary));
      }
      
      setLoading(false);
      navigate("/analysis");
    } catch (err) {
      setError(`Error: ${err.message}`);
      setLoading(false);
    }
  }

  function loadSample() {
    const sample = `transaction_id,sender_id,receiver_id,amount,timestamp
TX1,A,B,100,2026-02-01 09:00:00
TX2,B,C,50,2026-02-01 10:00:00
TX3,C,A,40,2026-02-01 11:00:00
TX4,X1,A,10,2026-02-01 12:00:00
TX5,X2,A,12,2026-02-02 12:00:00
TX6,X3,A,11,2026-02-03 12:00:00
TX7,S1,D,5,2026-02-05 08:00:00
TX8,S1,E,6,2026-02-05 09:00:00
TX9,S1,F,7,2026-02-05 10:00:00
TX10,S1,G,8,2026-02-05 11:00:00
TX11,S1,H,9,2026-02-05 12:00:00
TX12,S1,I,10,2026-02-05 12:30:00
`;
    const blob = new Blob([sample], { type: "text/csv" });
    onFile(blob);
  }

  function downloadSample() {
    const sample = `transaction_id,sender_id,receiver_id,amount,timestamp
TX1,A,B,100,2026-02-01 09:00:00
TX2,B,C,50,2026-02-01 10:00:00
TX3,C,A,40,2026-02-01 11:00:00
TX4,X1,A,10,2026-02-01 12:00:00
TX5,X2,A,12,2026-02-02 12:00:00
TX6,X3,A,11,2026-02-03 12:00:00
TX7,S1,D,5,2026-02-05 08:00:00
TX8,S1,E,6,2026-02-05 09:00:00
TX9,S1,F,7,2026-02-05 10:00:00
TX10,S1,G,8,2026-02-05 11:00:00
TX11,S1,H,9,2026-02-05 12:00:00
TX12,S1,I,10,2026-02-05 12:30:00
`;
    const blob = new Blob([sample], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "sample_transactions.csv";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex flex-col items-center justify-start px-4 py-16 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-pulse"></div>
      <div className="absolute top-0 right-0 w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-pulse animation-delay-2000"></div>
      <div className="absolute bottom-0 left-1/2 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-pulse animation-delay-4000"></div>

      {/* Header */}
      <div className="text-center mb-12 relative z-10 animate-fadeIn">
        <div className="flex items-center justify-center gap-3 mb-4">
          <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl shadow-lg shadow-blue-500/50">
            <FlaskConical size={24} className="text-white" />
          </div>
          <span className="text-lg font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">MuleX - Financial Forensics Engine</span>
        </div>

        <h1 className="text-6xl font-black bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-4 animate-fadeInUp">
          MONEY MULING DETECTION
        </h1>

        <p className="text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed animate-fadeInUp animation-delay-100">
          Advanced graph-based financial forensics engine that detects circular fund routing, 
          <span className="text-blue-400 font-semibold"> smurfing patterns</span>, and 
          <span className="text-purple-400 font-semibold"> shell networks</span> using real-time analysis.
        </p>
      </div>

      {/* Upload Box with Premium Styling */}
      <div className="w-full max-w-4xl mb-16 relative z-10 animate-fadeInUp animation-delay-200">
        {error && (
          <div className="mb-4 p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-400">
            {error}
          </div>
        )}
        
        <div
          className={`group relative ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
          onClick={() => !loading && fileInputRef.current?.click()}
          onDragOver={(e) => {
            if (!loading) {
              e.preventDefault();
              e.currentTarget.classList.add("scale-105");
            }
          }}
          onDragLeave={(e) => {
            e.currentTarget.classList.remove("scale-105");
          }}
          onDrop={(e) => {
            if (!loading) {
              e.preventDefault();
              e.currentTarget.classList.remove("scale-105");
              if (e.dataTransfer.files[0]) onFile(e.dataTransfer.files[0]);
            }
          }}
        >
          {/* Gradient Border */}
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-2xl blur-lg opacity-0 group-hover:opacity-75 transition duration-500 group-hover:duration-200"></div>
          
          {/* Content */}
          <div className="relative bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 group-hover:border-slate-600 rounded-2xl p-16 flex flex-col items-center justify-center transition-all duration-500 transform group-hover:scale-105 cursor-pointer">
            <div className="mb-6 p-4 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-xl group-hover:from-blue-500/30 group-hover:to-purple-500/30 transition-all duration-300">
              {loading ? (
                <Loader size={48} className="text-blue-400 animate-spin" />
              ) : (
                <Upload size={48} className="text-blue-400 group-hover:text-purple-400 transition-colors" />
              )}
            </div>

            <p className="font-bold text-2xl text-white mb-2 group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:from-blue-400 group-hover:to-purple-400 group-hover:bg-clip-text transition-all duration-300">
              {loading ? "Analyzing..." : "Drop your CSV file here"}
            </p>

            <p className="text-slate-400 group-hover:text-slate-300 mb-6 transition-colors">
              {loading ? "Processing with backend AI..." : "or click to browse (supports transaction data in standard format)"}
            </p>

            <p className="text-sm text-slate-500">
              Columns: <span className="text-blue-400 font-mono">transaction_id</span> • 
              <span className="text-purple-400 font-mono"> sender</span> • 
              <span className="text-pink-400 font-mono"> receiver</span> • 
              <span className="text-blue-400 font-mono"> amount</span> • 
              <span className="text-purple-400 font-mono"> timestamp</span>
            </p>

            <input
              ref={fileInputRef}
              type="file"
              accept="text/csv"
              onChange={(e) => {
                if (e.target.files[0]) onFile(e.target.files[0]);
              }}
              disabled={loading}
              className="hidden"
            />
          </div>
        </div>

        {/* Buttons */}
        <div className="flex gap-4 mt-8 justify-center animate-fadeInUp animation-delay-300">
          <button
            onClick={loadSample}
            disabled={loading}
            className={`group relative px-8 py-3 font-semibold text-white transition-all duration-300 overflow-hidden rounded-lg ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-blue-500 group-hover:to-purple-500 transition-all duration-300"></div>
            <div className="relative flex items-center gap-2">
              <Zap size={18} />
              Load Sample Data
            </div>
          </button>

          <button
            onClick={downloadSample}
            disabled={loading}
            className={`group px-8 py-3 font-semibold text-blue-400 border-2 border-blue-400 rounded-lg hover:bg-blue-400/10 hover:border-purple-400 hover:text-purple-400 transition-all duration-300 ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
          >
            <div className="flex items-center gap-2">
              <Download size={18} />
              Download Sample
            </div>
          </button>
        </div>
      </div>

      {/* Features Section with Cards */}
      <div className="flex gap-8 max-w-6xl w-full justify-between relative z-10 animate-fadeInUp animation-delay-400">
        {[
          {
            icon: <Shield size={28} />,
            title: "Cycle Detection",
            desc: "Identifies circular fund routing patterns (3–5 hops)",
            color: "from-blue-500 to-cyan-500"
          },
          {
            icon: <Zap size={28} />,
            title: "Smurfing Detection",
            desc: "Detects fan-in/out hubs within 72-hour windows",
            color: "from-purple-500 to-pink-500"
          },
          {
            icon: <Shield size={28} />,
            title: "Shell Networks",
            desc: "Maps pass-through layering chains and structures",
            color: "from-amber-500 to-orange-500"
          }
        ].map((feature, i) => (
          <div
            key={i}
            className="group flex-1 relative p-6 rounded-xl overflow-hidden transition-all duration-500 hover:scale-105 cursor-pointer"
          >
            <div className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300`}></div>
            <div className={`absolute inset-0 border border-slate-700 group-hover:border-slate-600 rounded-xl`}></div>
            
            <div className="relative">
              <div className={`inline-block p-3 bg-gradient-to-br ${feature.color} rounded-lg mb-3 text-white opacity-70 group-hover:opacity-100 transition-opacity`}>
                {feature.icon}
              </div>
              <h3 className="font-bold text-white mb-2 group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:from-blue-400 group-hover:to-purple-400 group-hover:bg-clip-text transition-all">
                {feature.title}
              </h3>
              <p className="text-slate-400 text-sm group-hover:text-slate-300 transition-colors">
                {feature.desc}
              </p>
            </div>
          </div>
        ))}
      </div>

      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.8s ease-out;
        }
        .animate-fadeInUp {
          animation: fadeInUp 0.8s ease-out forwards;
          opacity: 0;
        }
        .animation-delay-100 {
          animation-delay: 0.1s;
        }
        .animation-delay-200 {
          animation-delay: 0.2s;
        }
        .animation-delay-300 {
          animation-delay: 0.3s;
        }
        .animation-delay-400 {
          animation-delay: 0.4s;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  );
}
