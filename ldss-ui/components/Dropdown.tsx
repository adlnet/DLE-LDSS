'use client';

import React, { useState } from 'react';

export interface DropdownOption {
  id: string;
  name: string;
}

interface DropdownProps {
  label: string;
  onChange: (selectedOption: DropdownOption | null) => void;
  options?: DropdownOption[];
  value?: string
  disabled?: boolean
}

const Dropdown: React.FC<DropdownProps> = ({
  label,
  onChange,
  options = [],
  value,
  disabled = false,
}) => {
  const [selectedValue, setSelectedValue] = useState<DropdownOption | null>(null);

  const handleSelectOption = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const sel = options.find(o => o.id === e.target.value) || null;
    setSelectedValue(sel);
    onChange(sel);
  };

  return (
    <form className="flex items-center w-full">
      <label
        htmlFor={`select-${label}`}
        className={`block mr-2 text-sm font-medium ${disabled ? 'text-gray-500' : 'text-gray-900 dark:text-white'
          }`}
      >
        {label}
      </label>
      <select
        id={`select-${label}`}
        onChange={handleSelectOption}
        value={value || selectedValue?.id || ""}
        disabled={disabled}
        className={`
          max-w-sm block w-full text-sm rounded-lg

          bg-white border border-gray-300 text-gray-900
          hover:border-gray-400
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500

          dark:bg-gray-700 dark:border-gray-600 dark:text-white
          dark:hover:border-gray-500 dark:focus:ring-blue-500 dark:focus:border-blue-500

          disabled:bg-gray-200 disabled:border-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed
          dark:disabled:bg-gray-600 dark:disabled:border-gray-500 dark:disabled:text-gray-400
        `}
      >
        {!disabled && <option value="">Select {label}</option>}
        {options.map(opt => (
          <option key={opt.id} value={opt.id}>
            {opt.name}
          </option>
        ))}
      </select>
    </form>
  );
};

export default Dropdown;
