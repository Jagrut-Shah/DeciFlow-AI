"use client";

import React, { useState } from "react";
import Card from "@/components/Card";
import Button from "@/components/Button";

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);
    const [isDragging, setIsDragging] = useState(false);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            setFile(e.dataTransfer.files[0]);
            setIsSuccess(false);
        }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setFile(e.target.files[0]);
            setIsSuccess(false);
        }
    };

    const handleUpload = () => {
        if (!file) return;
        setIsUploading(true);
        // Simulate upload delay
        setTimeout(() => {
            setIsUploading(false);
            setIsSuccess(true);
            setFile(null); // Optional: clear file on success
        }, 2000);
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-[80vh] animate-in fade-in zoom-in-95 duration-700">
            <div className="text-center mb-8">
                <h1 className="text-4xl font-extrabold text-white mb-4">Data Ingestion Engine</h1>
                <p className="text-gray-400 max-w-xl mx-auto">
                    Upload your raw data securely. Our AI models will automatically process and detect actionable insights.
                </p>
            </div>

            <Card className="w-full max-w-xl p-8" glowOnHover={false}>
                <div
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={`
            border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300
            ${isDragging ? 'border-cyan-400 bg-cyan-400/10 shadow-[0_0_30px_rgba(34,211,238,0.2)]' : 'border-white/20 bg-white/5 hover:border-indigo-400 hover:bg-white/10'}
            ${isSuccess ? 'border-emerald-500/50 bg-emerald-500/10' : ''}
          `}
                >
                    {isSuccess ? (
                        <div className="flex flex-col items-center gap-4 animate-in zoom-in duration-500">
                            <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center">
                                <span className="text-3xl">✅</span>
                            </div>
                            <h3 className="text-2xl font-bold text-emerald-400">Upload Successful!</h3>
                            <p className="text-gray-300">Your dataset has been ingested and is being analyzed.</p>
                            <Button variant="secondary" className="mt-4" onClick={() => setIsSuccess(false)}>
                                Upload Another File
                            </Button>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center gap-4">
                            <div className="w-20 h-20 bg-gradient-to-tr from-cyan-500/20 to-indigo-500/20 rounded-full flex items-center justify-center shadow-inner">
                                <span className="text-4xl">📁</span>
                            </div>
                            <h3 className="text-2xl font-bold text-white">Upload your dataset</h3>
                            <p className="text-gray-400">Drag & drop your files here, or click to browse</p>

                            <input
                                type="file"
                                id="file-upload"
                                className="hidden"
                                onChange={handleFileChange}
                                accept=".csv, .xlsx"
                            />
                            <label htmlFor="file-upload">
                                <button className="mt-2 px-4 py-2 bg-cyan-500 rounded-xl hover:bg-cyan-600 transition">

                                    Browse Files
                                </button>
                            </label>

                            {file && (
                                <div className="mt-6 p-4 bg-[#111827] rounded-xl border border-white/10 flex items-center gap-3 w-full animate-in slide-in-from-bottom-2">
                                    <span className="text-2xl">📄</span>
                                    <div className="flex-1 text-left truncate">
                                        <p className="text-white font-medium truncate">{file.name}</p>
                                        <p className="text-xs text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                                    </div>
                                    <button onClick={() => setFile(null)} className="text-gray-500 hover:text-red-400">
                                        ✕
                                    </button>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {!isSuccess && (
                    <>
                        <div className="flex justify-between items-center mt-6 px-2 text-sm text-gray-500">
                            <span>CSV, XLSX supported</span>
                            <span>Max size 10MB</span>
                        </div>

                        <Button
                            className="w-full mt-6"
                            disabled={!file || isUploading}
                            onClick={handleUpload}
                        >
                            {isUploading ? (
                                <div className="flex items-center gap-2">
                                    <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Processing...
                                </div>
                            ) : (
                                "Upload and Analyze"
                            )}
                        </Button>
                    </>
                )}
            </Card>
        </div>
    );
}