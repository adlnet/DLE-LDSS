import { fireEvent, render, screen } from '@testing-library/react';
import CourseControls from './CourseControls';

describe('CourseControls', () => {
  it('renders with initial provider', () => {
    render(<CourseControls initialProvider="aetc" />);
    expect(screen.getByLabelText(/Source Provider/i)).toHaveValue('aetc');
  });

  it('changes target provider when dropdown changes', () => {
    render(<CourseControls initialProvider="jko" />);
    const dropdown = screen.getByLabelText(/Target Provider/i);
    fireEvent.change(dropdown, { target: { value: 'aetc' } });
    expect(dropdown).toHaveValue('aetc');
  });

  it('toggles language when button clicked', () => {
    render(<CourseControls initialProvider="aetc" />);
    const button = screen.getByRole('button');
    expect(screen.getByText('Source')).toBeInTheDocument();

    fireEvent.click(button);
    expect(screen.getByText('Target')).toBeInTheDocument();

    fireEvent.click(button);
    expect(screen.getByText('Source')).toBeInTheDocument();
  });
});