import React from "react";

const ClaimInput = ({value, onChange, disabled, showResults}) => {
  const placeholder = showResults
    ? "Enter a new claim to fact-check..."
    : "Enter a claim to fact-check (e.g., 'The Earth is flat', 'COVID-19 vaccines are effective')";

  return (
    <div>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        rows={showResults ? 3 : 4}
        className={`w-full p-4 border-2 rounded-xl resize-none transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
          disabled
            ? "bg-gray-50 border-gray-200 text-gray-500"
            : "border-gray-200 hover:border-gray-300 focus:border-blue-500"
        } ${showResults ? "text-base" : "text-lg"}`}
      />
    </div>
  );
};

export default ClaimInput;
