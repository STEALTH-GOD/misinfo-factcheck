import React from "react";
import {Search, Loader2} from "lucide-react";

const VerifyButton = ({loading, disabled, showResults}) => {
  return (
    <button
      type="submit"
      disabled={disabled || loading}
      className={`px-8 py-3 bg-blue-600 text-white rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
        disabled || loading
          ? "opacity-50 cursor-not-allowed"
          : "hover:bg-blue-700 hover:shadow-lg transform hover:-translate-y-0.5"
      } ${showResults ? "text-sm" : "text-lg"}`}
    >
      {loading ? (
        <>
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Verifying...</span>
        </>
      ) : (
        <>
          <Search className="w-5 h-5" />
          <span>{showResults ? "Verify New Claim" : "Verify Claim"}</span>
        </>
      )}
    </button>
  );
};

export default VerifyButton;
