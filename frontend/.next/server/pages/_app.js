"use strict";
/*
 * ATTENTION: An "eval-source-map" devtool has been used.
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file with attached SourceMaps in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
(() => {
var exports = {};
exports.id = "pages/_app";
exports.ids = ["pages/_app"];
exports.modules = {

/***/ "./src/pages/_app.tsx":
/*!****************************!*\
  !*** ./src/pages/_app.tsx ***!
  \****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": () => (/* binding */ App)\n/* harmony export */ });\n/* harmony import */ var react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react/jsx-dev-runtime */ \"react/jsx-dev-runtime\");\n/* harmony import */ var react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var styled_components__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! styled-components */ \"styled-components\");\n/* harmony import */ var styled_components__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(styled_components__WEBPACK_IMPORTED_MODULE_1__);\n/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react */ \"react\");\n/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_2__);\n/* harmony import */ var _styles_theme__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../styles/theme */ \"./src/styles/theme.ts\");\n\n\n\n\nconst GlobalStyle = (0,styled_components__WEBPACK_IMPORTED_MODULE_1__.createGlobalStyle)([\n    \":root{color-scheme:light dark;}*,*::before,*::after{box-sizing:border-box;}html,body,#__next{height:100%;}body{margin:0;font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Noto Sans,sans-serif;background:\",\n    \";color:\",\n    \";}a{color:inherit;text-decoration:none;}\"\n], (p)=>p.theme.colors.background, (p)=>p.theme.colors.text);\nfunction App({ Component, pageProps }) {\n    const [isDark, setIsDark] = (0,react__WEBPACK_IMPORTED_MODULE_2__.useState)(false);\n    (0,react__WEBPACK_IMPORTED_MODULE_2__.useEffect)(()=>{\n        const saved = localStorage.getItem(\"ignite-theme\");\n        setIsDark(saved === \"dark\");\n    }, []);\n    const toggle = ()=>{\n        const next = !isDark;\n        setIsDark(next);\n        localStorage.setItem(\"ignite-theme\", next ? \"dark\" : \"light\");\n    };\n    (0,react__WEBPACK_IMPORTED_MODULE_2__.useEffect)(()=>{\n        window.themeToggle = toggle;\n        return ()=>{\n            if (window.themeToggle === toggle) {\n                delete window.themeToggle;\n            }\n        };\n    }, [\n        toggle\n    ]);\n    return /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(styled_components__WEBPACK_IMPORTED_MODULE_1__.ThemeProvider, {\n        theme: {\n            ...isDark ? _styles_theme__WEBPACK_IMPORTED_MODULE_3__.darkTheme : _styles_theme__WEBPACK_IMPORTED_MODULE_3__.baseTheme,\n            toggleTheme: toggle\n        },\n        children: [\n            /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(GlobalStyle, {}, void 0, false, {\n                fileName: \"/Users/ishir/Desktop/IgniteCursor/frontend/src/pages/_app.tsx\",\n                lineNumber: 39,\n                columnNumber: 7\n            }, this),\n            /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(Component, {\n                ...pageProps\n            }, void 0, false, {\n                fileName: \"/Users/ishir/Desktop/IgniteCursor/frontend/src/pages/_app.tsx\",\n                lineNumber: 40,\n                columnNumber: 7\n            }, this)\n        ]\n    }, void 0, true, {\n        fileName: \"/Users/ishir/Desktop/IgniteCursor/frontend/src/pages/_app.tsx\",\n        lineNumber: 38,\n        columnNumber: 5\n    }, this);\n}\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvcGFnZXMvX2FwcC50c3giLCJtYXBwaW5ncyI6Ijs7Ozs7Ozs7Ozs7O0FBQ3FFO0FBQ3pCO0FBQ1c7QUFFdkQsTUFBTU0sY0FBY0wsb0VBQWlCQTs7OztHQUkrRyxDQUFDTSxJQUFNQSxFQUFFQyxLQUFLLENBQUNDLE1BQU0sQ0FBQ0MsVUFBVSxFQUFZLENBQUNILElBQU1BLEVBQUVDLEtBQUssQ0FBQ0MsTUFBTSxDQUFDRSxJQUFJO0FBSTNNLFNBQVNDLElBQUksRUFBRUMsU0FBUyxFQUFFQyxTQUFTLEVBQVk7SUFDNUQsTUFBTSxDQUFDQyxRQUFRQyxVQUFVLEdBQUdiLCtDQUFRQSxDQUFDO0lBRXJDRCxnREFBU0EsQ0FBQztRQUNSLE1BQU1lLFFBQVFDLGFBQWFDLE9BQU8sQ0FBQztRQUNuQ0gsVUFBVUMsVUFBVTtJQUN0QixHQUFHLEVBQUU7SUFFTCxNQUFNRyxTQUFTO1FBQ2IsTUFBTUMsT0FBTyxDQUFDTjtRQUNkQyxVQUFVSztRQUNWSCxhQUFhSSxPQUFPLENBQUMsZ0JBQWdCRCxPQUFPLFNBQVM7SUFDdkQ7SUFFQW5CLGdEQUFTQSxDQUFDO1FBQ1BxQixPQUFlQyxXQUFXLEdBQUdKO1FBQzlCLE9BQU87WUFDTCxJQUFJLE9BQWdCSSxXQUFXLEtBQUtKLFFBQVE7Z0JBQzFDLE9BQU8sT0FBZ0JJLFdBQVc7WUFDcEM7UUFDRjtJQUNGLEdBQUc7UUFBQ0o7S0FBTztJQUVYLHFCQUNFLDhEQUFDcEIsNERBQWFBO1FBQUNRLE9BQU87WUFBRSxHQUFJTyxTQUFTVixvREFBU0EsR0FBR0Qsb0RBQVM7WUFBR3FCLGFBQWFMO1FBQU87OzBCQUMvRSw4REFBQ2Q7Ozs7OzBCQUNELDhEQUFDTztnQkFBVyxHQUFHQyxTQUFTOzs7Ozs7Ozs7Ozs7QUFHOUIiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9pZ25pdGUta25vd2xlZGdlLWZyb250ZW5kLy4vc3JjL3BhZ2VzL19hcHAudHN4P2Y5ZDYiXSwic291cmNlc0NvbnRlbnQiOlsiaW1wb3J0IHR5cGUgeyBBcHBQcm9wcyB9IGZyb20gJ25leHQvYXBwJztcbmltcG9ydCB7IFRoZW1lUHJvdmlkZXIsIGNyZWF0ZUdsb2JhbFN0eWxlIH0gZnJvbSAnc3R5bGVkLWNvbXBvbmVudHMnO1xuaW1wb3J0IHsgdXNlRWZmZWN0LCB1c2VTdGF0ZSB9IGZyb20gJ3JlYWN0JztcbmltcG9ydCB7IGJhc2VUaGVtZSwgZGFya1RoZW1lIH0gZnJvbSAnLi4vc3R5bGVzL3RoZW1lJztcblxuY29uc3QgR2xvYmFsU3R5bGUgPSBjcmVhdGVHbG9iYWxTdHlsZWBcbiAgOnJvb3QgeyBjb2xvci1zY2hlbWU6IGxpZ2h0IGRhcms7IH1cbiAgKiwgKjo6YmVmb3JlLCAqOjphZnRlciB7IGJveC1zaXppbmc6IGJvcmRlci1ib3g7IH1cbiAgaHRtbCwgYm9keSwgI19fbmV4dCB7IGhlaWdodDogMTAwJTsgfVxuICBib2R5IHsgbWFyZ2luOiAwOyBmb250LWZhbWlseTogdWktc2Fucy1zZXJpZiwgc3lzdGVtLXVpLCAtYXBwbGUtc3lzdGVtLCBTZWdvZSBVSSwgUm9ib3RvLCBVYnVudHUsIENhbnRhcmVsbCwgTm90byBTYW5zLCBzYW5zLXNlcmlmOyBiYWNrZ3JvdW5kOiAkeyhwKSA9PiBwLnRoZW1lLmNvbG9ycy5iYWNrZ3JvdW5kfTsgY29sb3I6ICR7KHApID0+IHAudGhlbWUuY29sb3JzLnRleHR9OyB9XG4gIGEgeyBjb2xvcjogaW5oZXJpdDsgdGV4dC1kZWNvcmF0aW9uOiBub25lOyB9XG5gO1xuXG5leHBvcnQgZGVmYXVsdCBmdW5jdGlvbiBBcHAoeyBDb21wb25lbnQsIHBhZ2VQcm9wcyB9OiBBcHBQcm9wcykge1xuICBjb25zdCBbaXNEYXJrLCBzZXRJc0RhcmtdID0gdXNlU3RhdGUoZmFsc2UpO1xuXG4gIHVzZUVmZmVjdCgoKSA9PiB7XG4gICAgY29uc3Qgc2F2ZWQgPSBsb2NhbFN0b3JhZ2UuZ2V0SXRlbSgnaWduaXRlLXRoZW1lJyk7XG4gICAgc2V0SXNEYXJrKHNhdmVkID09PSAnZGFyaycpO1xuICB9LCBbXSk7XG5cbiAgY29uc3QgdG9nZ2xlID0gKCkgPT4ge1xuICAgIGNvbnN0IG5leHQgPSAhaXNEYXJrO1xuICAgIHNldElzRGFyayhuZXh0KTtcbiAgICBsb2NhbFN0b3JhZ2Uuc2V0SXRlbSgnaWduaXRlLXRoZW1lJywgbmV4dCA/ICdkYXJrJyA6ICdsaWdodCcpO1xuICB9O1xuXG4gIHVzZUVmZmVjdCgoKSA9PiB7XG4gICAgKHdpbmRvdyBhcyBhbnkpLnRoZW1lVG9nZ2xlID0gdG9nZ2xlO1xuICAgIHJldHVybiAoKSA9PiB7XG4gICAgICBpZiAoKHdpbmRvdyBhcyBhbnkpLnRoZW1lVG9nZ2xlID09PSB0b2dnbGUpIHtcbiAgICAgICAgZGVsZXRlICh3aW5kb3cgYXMgYW55KS50aGVtZVRvZ2dsZTtcbiAgICAgIH1cbiAgICB9O1xuICB9LCBbdG9nZ2xlXSk7XG5cbiAgcmV0dXJuIChcbiAgICA8VGhlbWVQcm92aWRlciB0aGVtZT17eyAuLi4oaXNEYXJrID8gZGFya1RoZW1lIDogYmFzZVRoZW1lKSwgdG9nZ2xlVGhlbWU6IHRvZ2dsZSB9fT5cbiAgICAgIDxHbG9iYWxTdHlsZSAvPlxuICAgICAgPENvbXBvbmVudCB7Li4ucGFnZVByb3BzfSAvPlxuICAgIDwvVGhlbWVQcm92aWRlcj5cbiAgKTtcbn1cblxuIl0sIm5hbWVzIjpbIlRoZW1lUHJvdmlkZXIiLCJjcmVhdGVHbG9iYWxTdHlsZSIsInVzZUVmZmVjdCIsInVzZVN0YXRlIiwiYmFzZVRoZW1lIiwiZGFya1RoZW1lIiwiR2xvYmFsU3R5bGUiLCJwIiwidGhlbWUiLCJjb2xvcnMiLCJiYWNrZ3JvdW5kIiwidGV4dCIsIkFwcCIsIkNvbXBvbmVudCIsInBhZ2VQcm9wcyIsImlzRGFyayIsInNldElzRGFyayIsInNhdmVkIiwibG9jYWxTdG9yYWdlIiwiZ2V0SXRlbSIsInRvZ2dsZSIsIm5leHQiLCJzZXRJdGVtIiwid2luZG93IiwidGhlbWVUb2dnbGUiLCJ0b2dnbGVUaGVtZSJdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./src/pages/_app.tsx\n");

/***/ }),

/***/ "./src/styles/theme.ts":
/*!*****************************!*\
  !*** ./src/styles/theme.ts ***!
  \*****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   baseTheme: () => (/* binding */ baseTheme),\n/* harmony export */   darkTheme: () => (/* binding */ darkTheme)\n/* harmony export */ });\nconst baseTheme = {\n    colors: {\n        background: \"linear-gradient(180deg, #E6F4F1 0%, #EAF3FF 100%)\",\n        surface: \"#ffffff\",\n        text: \"#0F2A43\",\n        primary: \"#1D74F5\",\n        secondary: \"#22C7A9\",\n        accent: \"#FF6B6B\",\n        muted: \"#6B7A90\",\n        border: \"#D7E2EE\",\n        cardBg: \"rgba(255,255,255,0.85)\"\n    },\n    radii: {\n        sm: \"8px\",\n        md: \"12px\",\n        lg: \"16px\",\n        xl: \"24px\"\n    },\n    shadows: {\n        sm: \"0 2px 8px rgba(0,0,0,0.06)\",\n        md: \"0 8px 24px rgba(16, 38, 73, 0.12)\"\n    },\n    transitions: {\n        base: \"200ms ease\"\n    }\n};\nconst darkTheme = {\n    ...baseTheme,\n    colors: {\n        ...baseTheme.colors,\n        background: \"linear-gradient(180deg, #0E1726 0%, #0D1B2A 100%)\",\n        surface: \"#0F253E\",\n        text: \"#EAF3FF\",\n        cardBg: \"rgba(19,33,53,0.85)\",\n        border: \"#1E3A5C\"\n    }\n};\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvc3R5bGVzL3RoZW1lLnRzIiwibWFwcGluZ3MiOiI7Ozs7O0FBQU8sTUFBTUEsWUFBWTtJQUN2QkMsUUFBUTtRQUNOQyxZQUFZO1FBQ1pDLFNBQVM7UUFDVEMsTUFBTTtRQUNOQyxTQUFTO1FBQ1RDLFdBQVc7UUFDWEMsUUFBUTtRQUNSQyxPQUFPO1FBQ1BDLFFBQVE7UUFDUkMsUUFBUTtJQUNWO0lBQ0FDLE9BQU87UUFDTEMsSUFBSTtRQUNKQyxJQUFJO1FBQ0pDLElBQUk7UUFDSkMsSUFBSTtJQUNOO0lBQ0FDLFNBQVM7UUFDUEosSUFBSTtRQUNKQyxJQUFJO0lBQ047SUFDQUksYUFBYTtRQUNYQyxNQUFNO0lBQ1I7QUFDRixFQUFXO0FBRUosTUFBTUMsWUFBWTtJQUN2QixHQUFHbkIsU0FBUztJQUNaQyxRQUFRO1FBQ04sR0FBR0QsVUFBVUMsTUFBTTtRQUNuQkMsWUFBWTtRQUNaQyxTQUFTO1FBQ1RDLE1BQU07UUFDTk0sUUFBUTtRQUNSRCxRQUFRO0lBQ1Y7QUFDRixFQUFXIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vaWduaXRlLWtub3dsZWRnZS1mcm9udGVuZC8uL3NyYy9zdHlsZXMvdGhlbWUudHM/NTE2MSJdLCJzb3VyY2VzQ29udGVudCI6WyJleHBvcnQgY29uc3QgYmFzZVRoZW1lID0ge1xuICBjb2xvcnM6IHtcbiAgICBiYWNrZ3JvdW5kOiAnbGluZWFyLWdyYWRpZW50KDE4MGRlZywgI0U2RjRGMSAwJSwgI0VBRjNGRiAxMDAlKScsXG4gICAgc3VyZmFjZTogJyNmZmZmZmYnLFxuICAgIHRleHQ6ICcjMEYyQTQzJyxcbiAgICBwcmltYXJ5OiAnIzFENzRGNScsIC8vIGJsdWVcbiAgICBzZWNvbmRhcnk6ICcjMjJDN0E5JywgLy8gbGlnaHQgZ3JlZW5cbiAgICBhY2NlbnQ6ICcjRkY2QjZCJyxcbiAgICBtdXRlZDogJyM2QjdBOTAnLFxuICAgIGJvcmRlcjogJyNEN0UyRUUnLFxuICAgIGNhcmRCZzogJ3JnYmEoMjU1LDI1NSwyNTUsMC44NSknXG4gIH0sXG4gIHJhZGlpOiB7XG4gICAgc206ICc4cHgnLFxuICAgIG1kOiAnMTJweCcsXG4gICAgbGc6ICcxNnB4JyxcbiAgICB4bDogJzI0cHgnXG4gIH0sXG4gIHNoYWRvd3M6IHtcbiAgICBzbTogJzAgMnB4IDhweCByZ2JhKDAsMCwwLDAuMDYpJyxcbiAgICBtZDogJzAgOHB4IDI0cHggcmdiYSgxNiwgMzgsIDczLCAwLjEyKSdcbiAgfSxcbiAgdHJhbnNpdGlvbnM6IHtcbiAgICBiYXNlOiAnMjAwbXMgZWFzZSdcbiAgfVxufSBhcyBjb25zdDtcblxuZXhwb3J0IGNvbnN0IGRhcmtUaGVtZSA9IHtcbiAgLi4uYmFzZVRoZW1lLFxuICBjb2xvcnM6IHtcbiAgICAuLi5iYXNlVGhlbWUuY29sb3JzLFxuICAgIGJhY2tncm91bmQ6ICdsaW5lYXItZ3JhZGllbnQoMTgwZGVnLCAjMEUxNzI2IDAlLCAjMEQxQjJBIDEwMCUpJyxcbiAgICBzdXJmYWNlOiAnIzBGMjUzRScsXG4gICAgdGV4dDogJyNFQUYzRkYnLFxuICAgIGNhcmRCZzogJ3JnYmEoMTksMzMsNTMsMC44NSknLFxuICAgIGJvcmRlcjogJyMxRTNBNUMnXG4gIH1cbn0gYXMgY29uc3Q7XG5cbmV4cG9ydCB0eXBlIFRoZW1lID0gdHlwZW9mIGJhc2VUaGVtZSAmIHsgdG9nZ2xlVGhlbWU/OiAoKSA9PiB2b2lkIH07XG5cbiJdLCJuYW1lcyI6WyJiYXNlVGhlbWUiLCJjb2xvcnMiLCJiYWNrZ3JvdW5kIiwic3VyZmFjZSIsInRleHQiLCJwcmltYXJ5Iiwic2Vjb25kYXJ5IiwiYWNjZW50IiwibXV0ZWQiLCJib3JkZXIiLCJjYXJkQmciLCJyYWRpaSIsInNtIiwibWQiLCJsZyIsInhsIiwic2hhZG93cyIsInRyYW5zaXRpb25zIiwiYmFzZSIsImRhcmtUaGVtZSJdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./src/styles/theme.ts\n");

/***/ }),

/***/ "react":
/*!************************!*\
  !*** external "react" ***!
  \************************/
/***/ ((module) => {

module.exports = require("react");

/***/ }),

/***/ "react/jsx-dev-runtime":
/*!****************************************!*\
  !*** external "react/jsx-dev-runtime" ***!
  \****************************************/
/***/ ((module) => {

module.exports = require("react/jsx-dev-runtime");

/***/ }),

/***/ "styled-components":
/*!************************************!*\
  !*** external "styled-components" ***!
  \************************************/
/***/ ((module) => {

module.exports = require("styled-components");

/***/ })

};
;

// load runtime
var __webpack_require__ = require("../webpack-runtime.js");
__webpack_require__.C(exports);
var __webpack_exec__ = (moduleId) => (__webpack_require__(__webpack_require__.s = moduleId))
var __webpack_exports__ = (__webpack_exec__("./src/pages/_app.tsx"));
module.exports = __webpack_exports__;

})();