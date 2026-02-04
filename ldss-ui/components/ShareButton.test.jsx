import '@testing-library/jest-dom';
import { render, screen, waitFor } from '@testing-library/react';
import ShareButton from './ShareButton';
import userEvent from '@testing-library/user-event';

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: jest.fn(),
  },
});

// Spy on log. 
const consoleSpy = jest.spyOn(console, 'count');

// Mock window.origin
beforeAll(() => {
  delete window.origin;
  window.origin = 'http://localhost';
});

describe('ShareButton Component', () => {
    //Test props.
    const basePropsTrue = {
    courseId: '123',
    courseTitle: 'Test class',
    courseDescription: 'A class to test the units.',
    user: true,
  };
  const basePropsFalse = {
    courseId: '123',
    courseTitle: 'Test class',
    courseDescription: 'A class to test the units.',
    user: false,
  };


  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the Share button with key layout classes', () => {
    
    const { container } = render(<ShareButton {...basePropsTrue}/>);

    const outer = container.querySelector('button');
    
    expect(outer).toHaveClass(
        'flex',
        'items-center',
        'gap-2',
        'min-w-max',
        'whitespace-nowrap',
        'p-2',
        'text-center',
        'text-white',
        'hover:shadow-md',
        'rounded-sm',
        'bg-blue-400',
        'hover:bg-blue-600',
        'font-medium',
        'transform',
        'transition-all',
        'duration-75',
        'ease-in-out',
        'focus:ring-2',
        'ring-blue-400',
        'outline-none'
      );
      
      expect(screen.getByRole('button', { name: /share/i })).toBeInTheDocument();
  });

  it('does not open modal or copy when user is false', async () => {
    render(<ShareButton {...basePropsFalse}/>);
    
    const buttonShare = await screen.findByRole('button', { name: /share/i });
    
    await userEvent.click(buttonShare);

   // Wait briefly to verify the modal never appears
   await waitFor(() => {

    // Make sure it was clicked, and the Modal/copy still didn't open:
    expect(consoleSpy).not.toHaveBeenCalled();

    expect(screen.queryByText(/link copied/i)).not.toBeInTheDocument();
  });
    expect(navigator.clipboard.writeText).not.toHaveBeenCalled();
  });

  it('copies link to clipboard and opens modal when user is true', async () => {
    
    render(<ShareButton {...basePropsTrue} />);

    const button = await screen.findByRole('button', { name: /share/i });
    
    await userEvent.click(button);

    // Wait for modal and clipboard interaction
  
  expect(consoleSpy).toHaveBeenCalledWith("share button clicked");
  expect(screen.getByText(/link copied/i)).toBeInTheDocument();
  expect(screen.getByText('http://localhost/course/123')).toBeInTheDocument();
  expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
    'http://localhost/course/123'
  );
  expect(navigator.clipboard.writeText).toHaveBeenCalledTimes(1);

});

it('opens a modal that has a Copy button, correctly rendered', async () => {
    
    const container = render(<ShareButton {...basePropsTrue}/>);
    
    const buttonShare = await screen.findByRole('button', { name: /share/i });

    
    await userEvent.click(buttonShare);

    // Now wait for the modal to show up
    const copyButton = await screen.findByRole('button', { name: /copy/i });
    
    expect(copyButton).toBeInTheDocument();
        
    expect(copyButton).toHaveClass(
            'inline-flex',
            'justify-center',
            'text-blue-900',
            'bg-blue-100',
            'hover:bg-blue-200'
        );
        
  });

  it('opens a modal that has a Copy button that writes to clipboard when clicked', async () => {
    render(<ShareButton {...basePropsTrue}/>);
    
    const buttonShare = await screen.findByRole('button', { name: /share/i });

    await userEvent.click(buttonShare);
    expect(consoleSpy).toHaveBeenCalledTimes(1);
    expect(consoleSpy).toHaveBeenCalledWith("share button clicked");
    const buttonCopy = screen.queryByRole('button', { name: /copy/i });
    await userEvent.click(buttonCopy);
    expect(navigator.clipboard.writeText).toHaveBeenCalledTimes(2);
      
});

it('opens a modal that has a Close button, correctly rendered', async () => {
    
    render(<ShareButton {...basePropsTrue}/>);
    
    const buttonShare = await screen.findByRole('button', { name: /share/i });

    await userEvent.click(buttonShare);

    const closeButton = await screen.findByRole('button', { name: /close/i });
    expect(closeButton).toBeInTheDocument();
        
    expect(closeButton).toHaveClass(
            'inline-flex',
            'justify-end',
            'text-blue-900',
            'bg-blue-100',
            'hover:bg-blue-200'
        );
      
  });

  it('opens a modal that closes when Close button is clicked', async () => {

    render(<ShareButton {...basePropsTrue}/>);
    
    const buttonShare = await screen.findByRole('button', { name: /share/i });

    await userEvent.click(buttonShare);

    expect(consoleSpy).toHaveBeenCalledTimes(1);
    expect(consoleSpy).toHaveBeenCalledWith("share button clicked");
    expect(screen.queryByRole('dialog')).toBeInTheDocument();

    const buttonClose = screen.queryByRole('button', { name: /close/i });
    await userEvent.click(buttonClose);
    expect(navigator.clipboard.writeText).toHaveBeenCalledTimes(1);  
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });

});


it('closes the modal when escape is pressed', async () => {
    
    render(<ShareButton {...basePropsTrue} />);
    
    const buttonShare = await screen.findByRole('button', { name: /share/i });
    
    await userEvent.click(buttonShare);

    expect(screen.getByRole('dialog')).toBeInTheDocument();
  
    await userEvent.keyboard('{Escape}');
  
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  
    expect(navigator.clipboard.writeText).toHaveBeenCalledTimes(1);
  });

    });

