module.exports = [
"[externals]/next/dist/shared/lib/no-fallback-error.external.js [external] (next/dist/shared/lib/no-fallback-error.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/shared/lib/no-fallback-error.external.js", () => require("next/dist/shared/lib/no-fallback-error.external.js"));

module.exports = mod;
}),
"[project]/Downloads/DeciFlow AI/frontend/app/app/favicon.ico (static in ecmascript, tag client)", ((__turbopack_context__) => {

__turbopack_context__.v("/_next/static/media/favicon.0x3dzn~oxb6tn.ico" + (globalThis["NEXT_CLIENT_ASSET_SUFFIX"] || ''));}),
"[project]/Downloads/DeciFlow AI/frontend/app/app/favicon.ico.mjs { IMAGE => \"[project]/Downloads/DeciFlow AI/frontend/app/app/favicon.ico (static in ecmascript, tag client)\" } [app-rsc] (structured image object, ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>__TURBOPACK__default__export__
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$app$2f$app$2f$favicon$2e$ico__$28$static__in__ecmascript$2c$__tag__client$29$__ = __turbopack_context__.i("[project]/Downloads/DeciFlow AI/frontend/app/app/favicon.ico (static in ecmascript, tag client)");
;
const __TURBOPACK__default__export__ = {
    src: __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$app$2f$app$2f$favicon$2e$ico__$28$static__in__ecmascript$2c$__tag__client$29$__["default"],
    width: 256,
    height: 256
};
}),
"[project]/Downloads/DeciFlow AI/frontend/app/components/Card.tsx [app-rsc] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>Card
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Downloads/DeciFlow AI/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/rsc/react-jsx-dev-runtime.js [app-rsc] (ecmascript)");
;
function Card({ children, className = '', glowOnHover = true }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: `
      bg-white/5 border border-white/10 backdrop-blur-lg rounded-2xl p-6
      transition-all duration-300 ease-in-out
      ${glowOnHover ? 'hover:bg-white/10 hover:shadow-[0_4px_30px_rgba(99,102,241,0.2)] hover:-translate-y-1' : ''}
      ${className}
    `,
        children: children
    }, void 0, false, {
        fileName: "[project]/Downloads/DeciFlow AI/frontend/app/components/Card.tsx",
        lineNumber: 11,
        columnNumber: 5
    }, this);
}
}),
"[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx [app-rsc] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>InsightsPage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Downloads/DeciFlow AI/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/rsc/react-jsx-dev-runtime.js [app-rsc] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$app$2f$components$2f$Card$2e$tsx__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Downloads/DeciFlow AI/frontend/app/components/Card.tsx [app-rsc] (ecmascript)");
;
;
function InsightsPage() {
    const insights = [
        {
            title: "Top Product",
            value: "Quantum Series X",
            detail: "32% of total revenue",
            icon: "🏆",
            gradient: "from-amber-400/20 to-orange-500/20",
            textColor: "text-amber-400"
        },
        {
            title: "Best Region",
            value: "North America",
            detail: "+18% YoY growth",
            icon: "🌎",
            gradient: "from-cyan-400/20 to-blue-500/20",
            textColor: "text-cyan-400"
        },
        {
            title: "Risk Alert",
            value: "Supply Chain",
            detail: "Logistics delay in EU",
            icon: "⚠️",
            gradient: "from-red-400/20 to-rose-500/20",
            textColor: "text-red-400"
        }
    ];
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "mb-10",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                        className: "text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400 pb-2",
                        children: "AI Insights 📊"
                    }, void 0, false, {
                        fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                        lineNumber: 35,
                        columnNumber: 17
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                        className: "text-gray-400 text-lg",
                        children: "Deep drill-down into your business metrics powered by Machine Learning."
                    }, void 0, false, {
                        fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                        lineNumber: 38,
                        columnNumber: 17
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                lineNumber: 34,
                columnNumber: 13
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "grid grid-cols-1 md:grid-cols-3 gap-6",
                children: insights.map((insight)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$app$2f$components$2f$Card$2e$tsx__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["default"], {
                        className: "p-6 relative overflow-hidden group",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: `absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl ${insight.gradient} rounded-bl-full opacity-50 transition-transform group-hover:scale-110 duration-500`
                            }, void 0, false, {
                                fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                                lineNumber: 44,
                                columnNumber: 25
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "relative z-10",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                        className: "text-4xl mb-4 block",
                                        children: insight.icon
                                    }, void 0, false, {
                                        fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                                        lineNumber: 46,
                                        columnNumber: 29
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("h3", {
                                        className: "text-lg text-gray-400 font-medium mb-1",
                                        children: insight.title
                                    }, void 0, false, {
                                        fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                                        lineNumber: 47,
                                        columnNumber: 29
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                        className: "text-2xl font-bold text-white mb-2",
                                        children: insight.value
                                    }, void 0, false, {
                                        fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                                        lineNumber: 48,
                                        columnNumber: 29
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                        className: `text-sm font-semibold ${insight.textColor}`,
                                        children: insight.detail
                                    }, void 0, false, {
                                        fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                                        lineNumber: 49,
                                        columnNumber: 29
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                                lineNumber: 45,
                                columnNumber: 25
                            }, this)
                        ]
                    }, insight.title, true, {
                        fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                        lineNumber: 43,
                        columnNumber: 21
                    }, this))
            }, void 0, false, {
                fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                lineNumber: 41,
                columnNumber: 13
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$app$2f$components$2f$Card$2e$tsx__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["default"], {
                className: "p-8 mt-8 border-indigo-500/30 bg-gradient-to-br from-indigo-900/10 to-purple-900/10 backdrop-blur-xl",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "flex items-start gap-4",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "w-12 h-12 rounded-2xl bg-indigo-500/20 flex items-center justify-center shrink-0 border border-indigo-500/30",
                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                className: "text-2xl",
                                children: "🤖"
                            }, void 0, false, {
                                fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                                lineNumber: 58,
                                columnNumber: 25
                            }, this)
                        }, void 0, false, {
                            fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                            lineNumber: 57,
                            columnNumber: 21
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                                    className: "text-2xl font-bold text-white mb-3",
                                    children: "AI Strategic Recommendation"
                                }, void 0, false, {
                                    fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                                    lineNumber: 61,
                                    columnNumber: 25
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                    className: "text-gray-300 leading-relaxed max-w-4xl text-lg mb-6",
                                    children: [
                                        "Based on the recent correlation between ",
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            className: "text-cyan-400 font-medium",
                                            children: "marketing spend in APAC"
                                        }, void 0, false, {
                                            fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                                            lineNumber: 63,
                                            columnNumber: 69
                                        }, this),
                                        " and the surging demand for ",
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            className: "text-amber-400 font-medium",
                                            children: "Quantum Series X"
                                        }, void 0, false, {
                                            fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                                            lineNumber: 63,
                                            columnNumber: 171
                                        }, this),
                                        ", our models predict a ",
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            className: "text-emerald-400 font-bold",
                                            children: "25% ROI increase"
                                        }, void 0, false, {
                                            fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                                            lineNumber: 63,
                                            columnNumber: 262
                                        }, this),
                                        " if you reallocate $15,000 from the EU logistics budget to APAC digital campaigns over the next 14 days."
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                                    lineNumber: 62,
                                    columnNumber: 25
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    className: "flex gap-4",
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            className: "px-6 py-2 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-semibold hover:scale-105 transition-transform shadow-[0_0_15px_rgba(99,102,241,0.5)]",
                                            children: "Execute Strategy"
                                        }, void 0, false, {
                                            fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                                            lineNumber: 66,
                                            columnNumber: 29
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Downloads$2f$DeciFlow__AI$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            className: "px-6 py-2 rounded-xl bg-white/5 border border-white/10 text-white font-semibold hover:bg-white/10 transition-colors",
                                            children: "View Detailed Model"
                                        }, void 0, false, {
                                            fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                                            lineNumber: 69,
                                            columnNumber: 29
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                                    lineNumber: 65,
                                    columnNumber: 25
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                            lineNumber: 60,
                            columnNumber: 21
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                    lineNumber: 56,
                    columnNumber: 17
                }, this)
            }, void 0, false, {
                fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
                lineNumber: 55,
                columnNumber: 13
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx",
        lineNumber: 33,
        columnNumber: 9
    }, this);
}
}),
"[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx [app-rsc] (ecmascript, Next.js Server Component)", ((__turbopack_context__) => {

__turbopack_context__.n(__turbopack_context__.i("[project]/Downloads/DeciFlow AI/frontend/app/app/insights/page.tsx [app-rsc] (ecmascript)"));
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__0k8it-y._.js.map