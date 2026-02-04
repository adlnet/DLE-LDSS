/**
 * @jest-environment jsdom
 */

import { render, screen } from '@testing-library/react';
import TablePage from './page';

// mock child components

jest.mock('../../../components/Header', () => {
  const MockHeader = () => <div data-testid="mock-header">Mock Header</div>;
  MockHeader.displayName = 'MockHeader';
  return MockHeader;
});

jest.mock('../../../components/Table', () => {
  const MockTable = () => <div data-testid="mock-table">Mock Table</div>;
  MockTable.displayName = 'MockTable';
  return MockTable;
});

describe('TablePage', () => {
  it('renders Header and Table inside main', () => {
    render(<TablePage />);

    expect(screen.getByTestId('mock-header')).toBeInTheDocument();

    const main = screen.getByRole('main');
    expect(main).toBeInTheDocument();
    expect(main).toHaveClass('container', 'mx-auto', 'p-16');

    expect(screen.getByTestId('mock-table')).toBeInTheDocument();
  });
});