import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import ConfigurationManager from '../ConfigurationManager';

// Mock axios
jest.mock('axios');

describe('ConfigurationManager Integration Tests', () => {
  const mockConfig = {
    openai_api_key: 'sk-test...xyz',
    firebase_project_id: 'test-project',
    google_analytics_id: 'GA-12345',
    google_ads_id: 'ADS-12345'
  };

  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  test('loads and displays configuration', async () => {
    // Mock the GET request
    axios.get.mockResolvedValueOnce({ data: mockConfig });

    render(<ConfigurationManager />);

    // Check loading state
    expect(screen.getByText('Loading configuration...')).toBeInTheDocument();

    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByText('Loading configuration...')).not.toBeInTheDocument();
    });

    // Check if fields are populated
    expect(screen.getByDisplayValue(mockConfig.firebase_project_id)).toBeInTheDocument();
    expect(screen.getByDisplayValue(mockConfig.google_analytics_id)).toBeInTheDocument();
    expect(screen.getByDisplayValue(mockConfig.google_ads_id)).toBeInTheDocument();
  });

  test('saves configuration successfully', async () => {
    // Mock the GET and POST requests
    axios.get.mockResolvedValueOnce({ data: mockConfig });
    axios.post.mockResolvedValueOnce({ data: { message: 'Configuration saved successfully' } });

    render(<ConfigurationManager />);

    // Wait for initial load
    await waitFor(() => {
      expect(screen.queryByText('Loading configuration...')).not.toBeInTheDocument();
    });

    // Update a field
    const firebaseInput = screen.getByPlaceholder('Enter Firebase Project ID');
    fireEvent.change(firebaseInput, { target: { value: 'new-project-id' } });

    // Submit the form
    const submitButton = screen.getByText('Save Configuration');
    fireEvent.click(submitButton);

    // Check loading state during save
    expect(screen.getByText('Loading configuration...')).toBeInTheDocument();

    // Wait for save to complete
    await waitFor(() => {
      expect(screen.getByText('Configuration saved successfully!')).toBeInTheDocument();
    });

    // Verify POST request was made with correct data
    expect(axios.post).toHaveBeenCalledWith('/api/configuration', {
      ...mockConfig,
      firebase_project_id: 'new-project-id'
    });
  });

  test('handles API errors gracefully', async () => {
    // Mock failed GET request
    axios.get.mockRejectedValueOnce(new Error('Failed to fetch configuration'));

    render(<ConfigurationManager />);

    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText('Error: Failed to fetch configuration')).toBeInTheDocument();
    });

    // Mock failed POST request
    axios.post.mockRejectedValueOnce(new Error('Failed to save configuration'));

    // Try to save
    const submitButton = screen.getByText('Save Configuration');
    fireEvent.click(submitButton);

    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText('Error: Failed to save configuration')).toBeInTheDocument();
    });
  });

  test('validates input fields', async () => {
    // Mock the GET request
    axios.get.mockResolvedValueOnce({ data: mockConfig });

    render(<ConfigurationManager />);

    // Wait for initial load
    await waitFor(() => {
      expect(screen.queryByText('Loading configuration...')).not.toBeInTheDocument();
    });

    // Test OpenAI API Key validation
    const openaiInput = screen.getByPlaceholder('Enter OpenAI API Key');
    fireEvent.change(openaiInput, { target: { value: 'invalid-key' } });

    // Submit form
    const submitButton = screen.getByText('Save Configuration');
    fireEvent.click(submitButton);

    // Mock validation response
    axios.post.mockResolvedValueOnce({
      data: {
        valid: false,
        errors: ['Invalid OpenAI API Key']
      }
    });

    // Wait for validation error
    await waitFor(() => {
      expect(screen.getByText('Error: Invalid OpenAI API Key')).toBeInTheDocument();
    });
  });

  test('maintains sensitive data masking', async () => {
    // Mock the GET request with masked API key
    axios.get.mockResolvedValueOnce({
      data: {
        ...mockConfig,
        openai_api_key: 'sk-test...xyz'
      }
    });

    render(<ConfigurationManager />);

    // Wait for initial load
    await waitFor(() => {
      expect(screen.queryByText('Loading configuration...')).not.toBeInTheDocument();
    });

    // Check if API key is masked
    const openaiInput = screen.getByPlaceholder('Enter OpenAI API Key');
    expect(openaiInput.value).toBe('sk-test...xyz');

    // Update API key
    fireEvent.change(openaiInput, { target: { value: 'sk-newkey123' } });

    // Submit form
    const submitButton = screen.getByText('Save Configuration');
    fireEvent.click(submitButton);

    // Verify the new key is sent in POST request
    expect(axios.post).toHaveBeenCalledWith('/api/configuration', {
      ...mockConfig,
      openai_api_key: 'sk-newkey123'
    });
  });
}); 