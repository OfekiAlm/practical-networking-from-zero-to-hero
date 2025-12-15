import React, { useState } from 'react';
import './DemoExecutor.css';
import { submitJob } from '../services/api';

const DemoExecutor = ({ demo, onJobCreated }) => {
  const [parameters, setParameters] = useState({});
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  const handleInputChange = (field, value) => {
    setParameters({
      ...parameters,
      [field]: value,
    });
    // Clear error for this field
    if (errors[field]) {
      setErrors({
        ...errors,
        [field]: null,
      });
    }
  };

  const validateParameters = () => {
    const newErrors = {};
    const schema = demo.parameters_schema;

    // Basic validation based on schema
    if (schema.required) {
      schema.required.forEach((field) => {
        if (!parameters[field]) {
          newErrors[field] = 'This field is required';
        }
      });
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateParameters()) {
      return;
    }

    setSubmitting(true);
    try {
      const job = await submitJob(demo.id, parameters);
      onJobCreated(job);
    } catch (err) {
      setErrors({
        _general: 'Failed to submit job: ' + err.message,
      });
    } finally {
      setSubmitting(false);
    }
  };

  const renderField = (fieldName, fieldSchema) => {
    const value = parameters[fieldName] || '';
    const error = errors[fieldName];
    const description = fieldSchema.description || '';
    const descriptionId = `${fieldName}-description`;
    const errorId = `${fieldName}-error`;

    let inputType = 'text';
    if (fieldSchema.type === 'integer' || fieldSchema.type === 'number') {
      inputType = 'number';
    }

    return (
      <div key={fieldName} className="form-field">
        <label htmlFor={fieldName}>
          {fieldName}
          {fieldSchema.required && <span className="required">*</span>}
        </label>
        {description && (
          <p id={descriptionId} className="field-description">
            {description}
          </p>
        )}
        <input
          id={fieldName}
          type={inputType}
          value={value}
          onChange={(e) => handleInputChange(fieldName, e.target.value)}
          placeholder={fieldSchema.examples?.[0] || ''}
          min={fieldSchema.minimum}
          max={fieldSchema.maximum}
          disabled={submitting}
          required={fieldSchema.required}
          aria-describedby={
            [description && descriptionId, error && errorId]
              .filter(Boolean)
              .join(' ') || undefined
          }
          aria-invalid={error ? 'true' : 'false'}
        />
        {error && (
          <span id={errorId} className="field-error" role="alert">
            {error}
          </span>
        )}
      </div>
    );
  };

  const schema = demo.parameters_schema;
  const properties = schema.properties || {};

  return (
    <div className="demo-executor">
      <div className="demo-header">
        <h2>{demo.name}</h2>
        <p className="demo-description">{demo.description}</p>
        <div className="demo-badges">
          <span className="badge">⏱️ Max {demo.max_runtime}s</span>
          {demo.requires_network && <span className="badge">🌐 Network</span>}
          {demo.requires_root && <span className="badge warning">🔒 Elevated</span>}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="demo-form">
        <h3>Parameters</h3>
        {Object.entries(properties).map(([fieldName, fieldSchema]) =>
          renderField(fieldName, fieldSchema)
        )}

        {errors._general && (
          <div className="form-error">{errors._general}</div>
        )}

        <button type="submit" disabled={submitting} className="submit-button">
          {submitting ? 'Submitting...' : 'Run Demo'}
        </button>
      </form>
    </div>
  );
};

export default DemoExecutor;
