"use client";

import React, { useState } from "react";
import Card from "@/components/Card";
import Button from "@/components/Button";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  FiUploadCloud,
  FiFile,
  FiCheckCircle,
  FiAlertCircle,
  FiDatabase,
} from "react-icons/fi";

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);
    const [isDragging, setIsDragging] = useState(false);
    const router = useRouter();

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

    const handleUpload = async () => {
        if (!file) return;
        setIsUploading(true);
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            // Ensure the API URL is constructed safely with fallbacks
            const baseUrl = (process.env.NEXT_PUBLIC_API_URL || '').replace(/\/$/, '');
            const endpoint = `${baseUrl}/api/v1/pipeline/execute-from-file`;

            const response = await fetch(
                endpoint,
                {
                    method: "POST",
                    body: formData,
                }
            );
            
            if (!response.ok) {
                let detailedErrorMessage = `Status: ${response.status} ${response.statusText}.`;
                try {
                    const errorData = await response.json();
                    if (errorData && errorData.detail) {
                        // Robustly handle FastAPI validation arrays or custom string errors
                        if (typeof errorData.detail === 'string') {
                            detailedErrorMessage = errorData.detail;
                        } else if (Array.isArray(errorData.detail)) {
                            detailedErrorMessage = errorData.detail
                                .map((err: { msg?: string } | string) => (typeof err === 'object' && err !== null && 'msg' in err ? err.msg : JSON.stringify(err)))
                                .join(", ");
                        } else {
                            detailedErrorMessage = JSON.stringify(errorData.detail);
                        }
                    } else if (errorData && errorData.message) { // Assuming backend might return 'message' for CustomException
                        detailedErrorMessage = errorData.message;
                    }
                } catch (jsonParseError) {
                    console.warn("Could not parse error response as JSON:", jsonParseError);
                }
                throw new Error(`Neural ingestion failed: ${detailedErrorMessage}`);
            }

            setIsSuccess(true);
            setFile(null);
            setTimeout(() => {
                router.push('/dashboard');
            }, 2000);
        } catch (error: unknown) { // Use unknown for better type safety
            setIsSuccess(false); // Ensure success state is false on error
            let displayMessage = "An unexpected error occurred during upload.";
            if (error instanceof Error) {
                displayMessage = error.message;
            } else if (typeof error === 'string') {
                displayMessage = error;
            }
            console.error("Upload error:", error);
            alert(`Error: ${displayMessage}`);
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto py-12 px-6">
            <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center mb-16"
            >
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-sapphire/10 border border-sapphire/20 text-sapphire text-[10px] font-black uppercase tracking-[0.3em] mb-6 shadow-2xl shadow-sapphire/10">
                    <FiDatabase className="animate-pulse" />
                    Ingestion Engine v3
                </div>
                <h1 className="text-5xl font-black text-navy dark:text-white mb-6 tracking-tight">
                    Strategic <span className="text-transparent bg-clip-text bg-gradient-to-r from-sapphire to-emerald">Data Ingestion</span>
                </h1>
                <p className="text-muted-text dark:text-white/40 text-lg max-w-2xl mx-auto font-medium leading-relaxed">
                    Securely bridge your raw operational data with our neural intelligence layer for real-time strategic synthesis.
                </p>
            </motion.div>

            <Card className="p-1.5 bg-white dark:bg-white/[0.03] border-cool-gray dark:border-white/10 rounded-[3rem] shadow-2xl overflow-hidden backdrop-blur-3xl">
                <div
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={`
                        relative rounded-[2.8rem] p-16 text-center transition-all duration-700
                        ${isDragging ? 'bg-sapphire/[0.04] scale-[0.98]' : 'bg-transparent'}
                    `}
                >
                    {/* Animated Border */}
                    <AnimatePresence>
                        {isDragging && (
                            <motion.div 
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="absolute inset-0 border-2 border-dashed border-sapphire/40 rounded-[2.8rem] animate-[spin_20s_linear_infinite]"
                            />
                        )}
                    </AnimatePresence>

                    <AnimatePresence mode="wait">
                        {isSuccess ? (
                            <motion.div 
                                key="success"
                                initial={{ opacity: 0, scale: 0.9, filter: "blur(10px)" }}
                                animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
                                className="flex flex-col items-center gap-8 py-10"
                            >
                                <div className="w-24 h-24 bg-emerald/10 border border-emerald/20 rounded-[2rem] flex items-center justify-center shadow-2xl shadow-emerald/10">
                                    <FiCheckCircle size={40} className="text-emerald" />
                                </div>
                                <div className="space-y-3">
                                    <h3 className="text-3xl font-black text-navy dark:text-white">Ingestion Complete</h3>
                                    <p className="text-muted-text dark:text-white/60 font-medium">Synchronizing with dashboard intelligence...</p>
                                </div>
                                <div className="w-64 h-1 bg-cool-gray dark:bg-white/5 rounded-full overflow-hidden">
                                    <motion.div 
                                        initial={{ x: "-100%" }}
                                        animate={{ x: "0%" }}
                                        transition={{ duration: 2, ease: "easeInOut" }}
                                        className="h-full bg-emerald"
                                    />
                                </div>
                            </motion.div>
                        ) : (
                            <motion.div 
                                key="input"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="flex flex-col items-center gap-8"
                            >
                                <motion.div 
                                    animate={isDragging ? { scale: 1.1, rotate: 5 } : {}}
                                    className={`w-28 h-28 rounded-[2.5rem] flex items-center justify-center transition-all duration-500 shadow-2xl ${
                                        isDragging ? 'bg-sapphire shadow-sapphire/40 text-white' : 'bg-white dark:bg-white/[0.05] border border-cool-gray dark:border-white/10 text-sapphire'
                                    }`}
                                >
                                    <FiUploadCloud size={48} className={isDragging ? 'animate-bounce' : ''} />
                                </motion.div>
                                
                                <div className="space-y-4">
                                    <h3 className="text-2xl font-black text-navy dark:text-white tracking-tight">Drop your Intelligence Source</h3>
                                    <p className="text-muted-text dark:text-white/40 font-medium max-w-xs mx-auto">
                                        Drag & drop CSV or JSON datasets, or <label htmlFor="file-upload" className="text-sapphire cursor-pointer hover:underline font-black italic">browse manually</label>
                                    </p>
                                </div>

                                <input
                                    type="file"
                                    id="file-upload"
                                    className="hidden"
                                    onChange={handleFileChange}
                                    accept=".csv, .json"
                                />

                                <AnimatePresence>
                                    {file && (
                                        <motion.div 
                                            initial={{ opacity: 0, y: 10, scale: 0.9 }}
                                            animate={{ opacity: 1, y: 0, scale: 1 }}
                                            exit={{ opacity: 0, scale: 0.9 }}
                                            className="w-full max-w-sm p-6 bg-white dark:bg-white/[0.05] border border-cool-gray dark:border-white/10 rounded-[2rem] flex items-center gap-5 shadow-2xl"
                                        >
                                            <div className="w-12 h-12 bg-sapphire/10 rounded-xl flex items-center justify-center text-sapphire">
                                                <FiFile size={24} />
                                            </div>
                                            <div className="flex-1 text-left min-w-0">
                                                <p className="text-navy dark:text-white font-black truncate">{file.name}</p>
                                                <p className="text-[10px] font-bold text-muted-text dark:text-white/30 uppercase tracking-widest">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                                            </div>
                                            <button 
                                                onClick={(e) => { e.stopPropagation(); setFile(null); }} 
                                                className="w-8 h-8 rounded-full hover:bg-alert-red/10 text-muted-text hover:text-alert-red transition-colors flex items-center justify-center"
                                            >
                                                ✕
                                            </button>
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                <AnimatePresence>
                    {!isSuccess && (
                        <motion.div 
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: "auto", opacity: 1 }}
                            className="px-10 pb-10 space-y-8"
                        >
                            <div className="flex justify-between items-center px-4 text-[10px] font-black text-muted-text dark:text-white/20 uppercase tracking-[0.2em]">
                                <div className="flex items-center gap-2">
                                    <FiCheckCircle className="text-emerald" />
                                    <span>Encrypted Transfer</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <FiAlertCircle className="text-amber" />
                                    <span>Max 10MB</span>
                                </div>
                            </div>

                            <Button
                                className="w-full py-6 text-lg font-black tracking-[0.2em] uppercase rounded-[2rem] shadow-2xl shadow-sapphire/20 relative overflow-hidden group"
                                disabled={!file || isUploading}
                                onClick={handleUpload}
                            >
                                <motion.div 
                                    animate={isUploading ? { x: ["-100%", "100%"] } : {}}
                                    transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
                                    className="absolute inset-0 bg-white/20 skew-x-12"
                                />
                                <span className="relative z-10 flex items-center justify-center gap-4">
                                    {isUploading ? (
                                        <>
                                            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                            <span>Processing Intelligence...</span>
                                        </>
                                    ) : "Initiate Ingestion"}
                                </span>
                            </Button>
                        </motion.div>
                    )}
                </AnimatePresence>
            </Card>
        </div>
    );
}
