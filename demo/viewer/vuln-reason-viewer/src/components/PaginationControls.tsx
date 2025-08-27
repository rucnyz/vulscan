// components/PaginationControls.tsx
import React, { useState, useEffect } from "react";

interface PaginationControlsProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  totalItems: number;
}

const PaginationControls: React.FC<PaginationControlsProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  totalItems,
}) => {
  const [pageInput, setPageInput] = useState<string>(
    (currentPage + 1).toString()
  );

  // Update input when currentPage changes externally
  useEffect(() => {
    setPageInput((currentPage + 1).toString());
  }, [currentPage]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Allow only numeric input
    const value = e.target.value.replace(/[^0-9]/g, "");
    setPageInput(value);
  };

  const handleInputBlur = () => {
    let pageNum = parseInt(pageInput, 10);

    // Handle invalid input
    if (isNaN(pageNum) || pageInput === "") {
      setPageInput((currentPage + 1).toString());
      return;
    }

    // Ensure page is within bounds
    if (pageNum < 1) pageNum = 1;
    if (pageNum > totalPages) pageNum = totalPages;

    // Update state and navigate to page
    setPageInput(pageNum.toString());
    onPageChange(pageNum - 1); // Adjust to 0-based index
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.currentTarget.blur(); // Trigger the blur event
    }
  };

  return (
    <div className="flex flex-col sm:flex-row justify-between items-center">
      <div className="text-sm text-gray-700 mb-2 sm:mb-0">
        Showing result {currentPage + 1} of {totalItems}{" "}
        {totalItems === 1 ? "entry" : "entries"}
      </div>

      <div className="flex items-center space-x-1">
        <button
          onClick={() => onPageChange(0)}
          disabled={currentPage === 0}
          className="px-3 py-1 rounded border border-gray-300 disabled:opacity-50"
        >
          First
        </button>
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 0}
          className="px-3 py-1 rounded border border-gray-300 disabled:opacity-50"
        >
          Previous
        </button>

        <div className="flex items-center border border-gray-300 rounded bg-gray-50 px-1">
          <input
            type="text"
            value={pageInput}
            onChange={handleInputChange}
            onBlur={handleInputBlur}
            onKeyPress={handleKeyPress}
            className="w-10 px-1 py-1 text-center bg-transparent"
            aria-label="Go to page"
          />
          <span className="px-1">/</span>
          <span className="px-1">{totalPages}</span>
        </div>

        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage >= totalPages - 1}
          className="px-3 py-1 rounded border border-gray-300 disabled:opacity-50"
        >
          Next
        </button>
        <button
          onClick={() => onPageChange(totalPages - 1)}
          disabled={currentPage >= totalPages - 1}
          className="px-3 py-1 rounded border border-gray-300 disabled:opacity-50"
        >
          Last
        </button>
      </div>
    </div>
  );
};

export default PaginationControls;
