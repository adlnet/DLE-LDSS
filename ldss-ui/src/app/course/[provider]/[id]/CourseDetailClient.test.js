import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import CourseDetailClient from './CourseDetailClient';

const mockCourse = {
  course_name: 'Test Course',
  agency_organization: 'Air Force',
  course_description: 'A sample description',
  course_material_format: 'Online',
  course_administered_location: 'Virtual',
  instance: 'Main',
  delivery_mode: 'Self-paced',
  comments: 'This is a comment',
};

describe('CourseDetailClient', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    global.fetch = jest.fn(); // stub fetch for every test
  });

  it('renders course details', () => {
    render(
      <CourseDetailClient initialCourse={mockCourse} initialProvider="aetc" />
    );
    expect(screen.getByText(/Test Course/i)).toBeInTheDocument();
    expect(screen.getByText(/Air Force/i)).toBeInTheDocument();
    expect(screen.getByText(/Self-paced/i)).toBeInTheDocument();
    expect(screen.getByText(/This is a comment/i)).toBeInTheDocument();
  });

  it('toggles language', () => {
    render(
      <CourseDetailClient initialCourse={mockCourse} initialProvider="aetc" />
    );
    const button = screen.getByRole('button');
    expect(screen.getByText('Source')).toBeInTheDocument();
    fireEvent.click(button);
    expect(screen.getByText('Target')).toBeInTheDocument();
  });

  it('loads instances from API', async () => {
    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          inst1: { url: 'aetc', name: 'aetc', displayName: 'AETC' },
          inst2: { url: 'jko', name: 'jko', displayName: 'JKO' },
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [
          { source: { alias: 'Agency' }, target: { alias: 'Org' } },
        ],
      });

    render(
      <CourseDetailClient initialCourse={mockCourse} initialProvider="aetc" />
    );

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/instances'),
        expect.anything()
      );
      expect(screen.getByLabelText(/Target Provider/i)).toHaveValue('jko');
    });
  });

  it('handles instance fetch error gracefully', async () => {
    global.fetch.mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => ({}),
    });

    render(
      <CourseDetailClient initialCourse={mockCourse} initialProvider="aetc" />
    );

    await waitFor(() => {
      expect(screen.getByLabelText(/Target Provider/i)).toBeInTheDocument();
    });
  });
});
