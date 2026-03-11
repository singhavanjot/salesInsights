import React, { useState } from 'react';

const EmailInput = ({ value, onChange, disabled }) => {
  const [isValid, setIsValid] = useState(true);
  const [touched, setTouched] = useState(false);

  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

  const handleChange = (e) => {
    const newValue = e.target.value;
    onChange(newValue);
    
    if (touched) {
      setIsValid(emailRegex.test(newValue) || newValue === '');
    }
  };

  const handleBlur = () => {
    setTouched(true);
    setIsValid(emailRegex.test(value) || value === '');
  };

  return (
    <div className="email-input-container">
      <label htmlFor="email" className="email-label">
        📧 Recipient Email
      </label>
      <div className="email-input-wrapper">
        <input
          id="email"
          type="email"
          value={value}
          onChange={handleChange}
          onBlur={handleBlur}
          disabled={disabled}
          placeholder="Enter email to receive the report"
          className={`email-input ${touched && !isValid ? 'invalid' : ''}`}
          autoComplete="email"
        />
        {value && (
          <span className={`email-status ${isValid ? 'valid' : 'invalid'}`}>
            {isValid ? '✓' : '✗'}
          </span>
        )}
      </div>
      {touched && !isValid && value && (
        <span className="email-error">
          Please enter a valid email address
        </span>
      )}
    </div>
  );
};

export default EmailInput;
