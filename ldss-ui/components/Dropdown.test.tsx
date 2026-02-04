import { fireEvent, render, screen } from '@testing-library/react';
import Dropdown, { DropdownOption } from './Dropdown';
import React from 'react';

describe('Dropdown Component', () => {
  const options: DropdownOption[] = [
    { id: '1', name: 'Option 1' },
    { id: '2', name: 'Option 2' },
  ];

  test('renders the label and default option', () => {
    render(<Dropdown label="Test" onChange={jest.fn()} options={options} />);
    
    // Check for the label
    expect(screen.getByLabelText(/Test/)).toBeInTheDocument();
    
    // Check for the default select option
    expect(screen.getByRole('option', { name: 'Select Test' })).toBeInTheDocument();
  });

  test('renders all provided options', () => {
    render(<Dropdown label="Test" onChange={jest.fn()} options={options} />);
    
    // Each option from the options array should be rendered
    options.forEach(option => {
      expect(screen.getByRole('option', { name: option.name })).toBeInTheDocument();
    });
  });

  test('calls onChange with the selected option', () => {
    const onChangeMock = jest.fn();
    render(<Dropdown label="Test" onChange={onChangeMock} options={options} />);
    
    const selectElement = screen.getByLabelText(/Test/);
    
    // Simulate selecting the first option
    fireEvent.change(selectElement, { target: { value: '1' } });
    expect(onChangeMock).toHaveBeenCalledWith(options[0]);
    
    // Simulate selecting the default (blank) option
    fireEvent.change(selectElement, { target: { value: '' } });
    expect(onChangeMock).toHaveBeenCalledWith(null);
  });

  test('renders only the default option when no options are provided', () => {
    render(<Dropdown label="Test" onChange={jest.fn()} />);
    
    // With no options provided, only the default option should appear
    expect(screen.getByRole('option', { name: 'Select Test' })).toBeInTheDocument();

    // There should be exactly one option in the select
    expect(screen.getAllByRole('option')).toHaveLength(1);

    });

    // Added these to make more thorough - MB
    test('disables the dropdown when the disabled prop is true', () => {
      render(
        <Dropdown
          label="Test"
          onChange={jest.fn()}
          options={options}
          disabled
        />
      );
    
      expect(screen.getByLabelText(/Test/)).toBeDisabled();
  });

  it('shows the correct option based on the value prop', () => {
    render(
      <Dropdown
        label="Test"
        onChange={jest.fn()}
        options={options}
        value="2"
      />
    );
  
    expect(screen.getByDisplayValue('Option 2')).toBeInTheDocument();
  });

  it('applies key styling classes to the select element', () => {
    render(<Dropdown label="Test" onChange={jest.fn()} options={options} />);
    
    const select = screen.getByLabelText(/Test/);
    expect(select).toHaveClass('max-w-sm');
    expect(select).toHaveClass('disabled:cursor-not-allowed');
  });
  
});
