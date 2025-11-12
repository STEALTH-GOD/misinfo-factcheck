import React from "react";
import {CheckCircle, XCircle, AlertCircle, Info} from "lucide-react";

const StatusBadge = ({verdict}) => {
  const getStatusConfig = (verdict) => {
    switch (verdict) {
      case "TRUE":
        return {
          icon: CheckCircle,
          text: "True",
          bgColor: "bg-green-100",
          textColor: "text-green-800",
          borderColor: "border-green-200",
        };
      case "FALSE":
        return {
          icon: XCircle,
          text: "False",
          bgColor: "bg-red-100",
          textColor: "text-red-800",
          borderColor: "border-red-200",
        };
      case "MISLEADING":
        return {
          icon: AlertCircle,
          text: "Mixed Evidence",
          bgColor: "bg-yellow-100",
          textColor: "text-yellow-800",
          borderColor: "border-yellow-200",
        };
      case "UNCLEAR":
      default:
        return {
          icon: Info,
          text: "Unverified",
          bgColor: "bg-gray-100",
          textColor: "text-gray-800",
          borderColor: "border-gray-200",
        };
    }
  };

  const config = getStatusConfig(verdict);
  const IconComponent = config.icon;

  return (
    <div
      className={`inline-flex items-center space-x-2 px-4 py-2 rounded-full border ${config.bgColor} ${config.textColor} ${config.borderColor}`}
    >
      <IconComponent className="w-5 h-5" />
      <span className="font-semibold text-lg">{config.text}</span>
    </div>
  );
};

export default StatusBadge;
