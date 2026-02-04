import { fireEvent, render, screen } from '@testing-library/react';
import { usePathname, useRouter } from 'next/navigation';
import Home from '../app/page';
import userEvent from '@testing-library/user-event';

jest.mock('next/navigation', () => ({
    useRouter: jest.fn(),
    usePathname: jest.fn(),
  }));

describe('Home Page', () => {
  
  const push = jest.fn();

  beforeEach(() => {

    push.mockClear();
    (useRouter).mockReturnValue({ push });
    (usePathname).mockReturnValue('/'); 
  });
  it('renders input and search button', () => {
    render(<Home />);
    expect(screen.getByPlaceholderText(/search courses/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /search/i })).toBeInTheDocument();
  });
  

  it('performs search on valid input', () => {
    render(<Home />);
    const input = screen.getByPlaceholderText(/search courses/i);
    const button = screen.getByRole('button', { name: /search/i });
    const keyword = 'test course';

    fireEvent.change(input, { target: { value: keyword } });
    fireEvent.click(button);

    const encodedWord = `/search?keyword=${encodeURIComponent(keyword.trim())}`;
    expect(push).toHaveBeenCalledWith(encodedWord);
  });

  it('shows error if input exceeds 250 characters', async () => {
    render(<Home />);
    const input = screen.getByPlaceholderText(/search courses/i);
    const button = screen.getByRole('button', { name: /search/i });

    const keyword = 'a'.repeat(251);
    await userEvent.type(input, keyword);
    fireEvent.click(button);
    expect(screen.getByText(/search is too long/i)).toBeInTheDocument();
    expect(push).not.toHaveBeenCalled();
  });

  it('does not push on empty input', () => {
    render(<Home />);
    const input = screen.getByPlaceholderText(/search courses/i);
    const button = screen.getByRole('button', { name: /search/i });
    const keyword = '';
    fireEvent.change(input, { target: { value: keyword} });
    fireEvent.click(button)
    expect(push).not.toHaveBeenCalled();
  })

  it('performs search when pressing Enter', async () => {
    render(<Home />);
    const input = screen.getByPlaceholderText(/search courses/i);
  
    const keyword = 'enter key test';
    await userEvent.type(input, keyword);
    await userEvent.keyboard('{Enter}');
  
    const expectedURL = `/search?keyword=${encodeURIComponent(keyword.trim())}`;
    expect(push).toHaveBeenCalledWith(expectedURL);
  });
  
});
