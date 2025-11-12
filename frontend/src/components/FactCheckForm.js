import React from "react";
import ClaimInput from "./ClaimInput";
import VerifyButton from "./VerifyButton";

const FactCheckForm = ({
  claim,
  setClaim,
  onVerify,
  loading,
  showResults,
  onNewClaim,
}) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (claim.trim() && !loading) {
      onVerify(claim.trim());
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-card p-8 mb-8">
      <form onSubmit={handleSubmit} className="space-y-6">
        <ClaimInput
          value={claim}
          onChange={setClaim}
          disabled={loading}
          showResults={showResults}
        />

        <div className="flex justify-center space-x-4">
          <VerifyButton
            loading={loading}
            disabled={!claim.trim()}
            showResults={showResults}
          />

          {showResults && (
            <button
              type="button"
              onClick={onNewClaim}
              className="px-8 py-3 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors duration-200"
            >
              New Claim
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default FactCheckForm;
