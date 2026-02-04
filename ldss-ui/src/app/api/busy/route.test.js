/**
 * @jest-environment node
 */

import { GET } from './route';
import toobusy from 'toobusy-js';

jest.mock('toobusy-js', () => ({
  __esModule: true,
  default: jest.fn(),
}));

describe('GET /api/health (toobusy)', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('returns 503 when server is busy', async () => {
    (toobusy).mockReturnValue(true);

    const res = await GET();

    expect(res.status).toBe(503);
    await expect(res.text()).resolves.toBe('Server busy');
    expect(toobusy).toHaveBeenCalledTimes(1);
  });

  it('returns 200 OK when not busy', async () => {
    (toobusy).mockReturnValue(false);

    const res = await GET();

    expect(res.status).toBe(200);
    await expect(res.text()).resolves.toBe('OK');
    expect(toobusy).toHaveBeenCalledTimes(1);
  });
});
