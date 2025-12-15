import React, { useState, useEffect } from 'react';
import './JobStatus.css';
import { getJobStatus } from '../services/api';

const JobStatus = ({ jobId, demoId }) => {
  const [job, setJob] = useState(null);
  const [error, setError] = useState(null);
  const [polling, setPolling] = useState(true);

  useEffect(() => {
    let interval;

    const fetchStatus = async () => {
      try {
        const data = await getJobStatus(jobId);
        setJob(data);
        setError(null);

        // Stop polling if job is completed or failed
        if (['completed', 'failed', 'timeout'].includes(data.status)) {
          setPolling(false);
        }
      } catch (err) {
        setError('Failed to fetch job status: ' + err.message);
        setPolling(false);
      }
    };

    fetchStatus();

    if (polling) {
      interval = setInterval(fetchStatus, 2000); // Poll every 2 seconds
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [jobId, polling]);

  if (error) {
    return (
      <div className="job-status">
        <div className="error-box">{error}</div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="job-status">
        <div className="loading-box">Loading job status...</div>
      </div>
    );
  }

  const statusColors = {
    pending: '#ffa500',
    running: '#4a90e2',
    completed: '#28a745',
    failed: '#dc3545',
    timeout: '#6c757d',
  };

  const statusIcons = {
    pending: '⏳',
    running: '⚙️',
    completed: '✅',
    failed: '❌',
    timeout: '⏱️',
  };

  const renderResult = () => {
    if (!job.result) return null;

    return (
      <div className="result-section">
        <h3>Results</h3>
        {job.result.error && (
          <div className="error-box">
            <strong>Error:</strong> {job.result.error}
          </div>
        )}
        {job.result.data && (
          <div className="result-data">
            <pre>{JSON.stringify(job.result.data, null, 2)}</pre>
          </div>
        )}
        {job.result.metadata && (
          <div className="metadata">
            <h4>Execution Metadata</h4>
            <div className="metadata-grid">
              {Object.entries(job.result.metadata).map(([key, value]) => (
                <div key={key} className="metadata-item">
                  <span className="metadata-key">{key}:</span>
                  <span className="metadata-value">{JSON.stringify(value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="job-status">
      <div className="status-header">
        <h2>Job Status</h2>
        <div
          className="status-badge"
          style={{ backgroundColor: statusColors[job.status] }}
        >
          {statusIcons[job.status]} {job.status.toUpperCase()}
        </div>
      </div>

      <div className="job-info">
        <div className="info-item">
          <strong>Job ID:</strong> <code>{job.job_id}</code>
        </div>
        <div className="info-item">
          <strong>Demo:</strong> {job.demo_id}
        </div>
        <div className="info-item">
          <strong>Created:</strong> {new Date(job.created_at).toLocaleString()}
        </div>
        {job.started_at && (
          <div className="info-item">
            <strong>Started:</strong> {new Date(job.started_at).toLocaleString()}
          </div>
        )}
        {job.completed_at && (
          <div className="info-item">
            <strong>Completed:</strong> {new Date(job.completed_at).toLocaleString()}
          </div>
        )}
      </div>

      {polling && (
        <div className="polling-indicator">
          <div className="spinner"></div>
          <span>Polling for updates...</span>
        </div>
      )}

      {renderResult()}
    </div>
  );
};

export default JobStatus;
