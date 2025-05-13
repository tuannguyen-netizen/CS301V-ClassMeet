import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './component/App';

test('renders video call and chat box', () => {
  render(<App />);
  const videoCallElement = screen.getByText(/video call/i);
  const chatBoxElement = screen.getByText(/chat box/i);
  expect(videoCallElement).toBeInTheDocument();
  expect(chatBoxElement).toBeInTheDocument();
});