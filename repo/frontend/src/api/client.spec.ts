import { afterEach, describe, expect, it, vi } from 'vitest'
import axios, { AxiosError, type AxiosAdapter, type AxiosRequestConfig } from 'axios'

import api, {
  extractApiError,
  setAccessToken,
  setUnauthorizedHandler,
  unwrap,
} from './client'

type CapturedRequest = { config: AxiosRequestConfig }

function installAdapter(handler: (config: AxiosRequestConfig) => Promise<any> | any): {
  captured: CapturedRequest[]
  restore: () => void
} {
  const captured: CapturedRequest[] = []
  const previous = api.defaults.adapter
  const adapter: AxiosAdapter = async (config) => {
    captured.push({ config })
    const result = await handler(config)
    return {
      status: result?.status ?? 200,
      statusText: result?.statusText ?? 'OK',
      headers: result?.headers ?? {},
      data: result?.data ?? null,
      config,
      request: {},
    }
  }
  api.defaults.adapter = adapter
  return {
    captured,
    restore: () => {
      api.defaults.adapter = previous
    },
  }
}

describe('api client interceptors', () => {
  afterEach(() => {
    setAccessToken('')
    setUnauthorizedHandler(async () => {})
  })

  it('attaches the bearer access token set via setAccessToken', async () => {
    setAccessToken('abc.token.xyz')
    const { captured, restore } = installAdapter(() => ({
      data: { success: true, data: { ok: true } },
    }))
    try {
      const response = await api.get('/echo')
      expect(response.status).toBe(200)
      expect(captured[0].config.headers?.Authorization).toBe('Bearer abc.token.xyz')
    } finally {
      restore()
    }
  })

  it('omits the Authorization header when no token is set', async () => {
    setAccessToken('')
    const { captured, restore } = installAdapter(() => ({
      data: { success: true, data: { ok: true } },
    }))
    try {
      await api.get('/anonymous')
      expect(captured[0].config.headers?.Authorization).toBeUndefined()
    } finally {
      restore()
    }
  })

  it('invokes the unauthorized handler on a 401 response and rejects the promise', async () => {
    const handler = vi.fn(async () => {})
    setUnauthorizedHandler(handler)
    const { restore } = installAdapter(() => {
      return Promise.reject(
        new AxiosError(
          'Unauthorized',
          'ERR_BAD_REQUEST',
          undefined,
          null,
          {
            status: 401,
            statusText: 'Unauthorized',
            headers: {},
            data: {},
            config: {} as any,
          } as any,
        ),
      )
    })
    try {
      await expect(api.get('/secure')).rejects.toBeInstanceOf(AxiosError)
      expect(handler).toHaveBeenCalledTimes(1)
    } finally {
      restore()
    }
  })

  it('does not invoke the unauthorized handler on 500 errors', async () => {
    const handler = vi.fn(async () => {})
    setUnauthorizedHandler(handler)
    const { restore } = installAdapter(() => {
      return Promise.reject(
        new AxiosError(
          'Server error',
          'ERR_BAD_RESPONSE',
          undefined,
          null,
          {
            status: 500,
            statusText: 'Internal Server Error',
            headers: {},
            data: {},
            config: {} as any,
          } as any,
        ),
      )
    })
    try {
      await expect(api.get('/broken')).rejects.toBeInstanceOf(AxiosError)
      expect(handler).not.toHaveBeenCalled()
    } finally {
      restore()
    }
  })
})

describe('unwrap helper', () => {
  it('extracts the data field from a success envelope', async () => {
    const extracted = await unwrap<{ id: string }>(
      Promise.resolve({
        data: { success: true, message: 'ok', data: { id: 'abc' } },
      }),
    )
    expect(extracted).toEqual({ id: 'abc' })
  })

  it('propagates the underlying rejection', async () => {
    const err = new Error('network down')
    await expect(unwrap(Promise.reject(err))).rejects.toThrow('network down')
  })
})

describe('extractApiError helper', () => {
  it('returns the first backend error detail when available', () => {
    const error = new AxiosError(
      'Request failed',
      'ERR_BAD_REQUEST',
      undefined,
      null,
      {
        status: 422,
        statusText: 'Unprocessable Entity',
        headers: {},
        data: {
          success: false,
          message: 'validation failed',
          errors: [{ code: 'invalid', detail: 'field is required' }],
        },
        config: {} as any,
      } as any,
    )
    expect(extractApiError(error)).toBe('field is required')
  })

  it('falls back to the envelope message when no error detail is present', () => {
    const error = new AxiosError(
      'Request failed',
      'ERR_BAD_REQUEST',
      undefined,
      null,
      {
        status: 400,
        statusText: 'Bad Request',
        headers: {},
        data: { success: false, message: 'bad request payload', errors: [] },
        config: {} as any,
      } as any,
    )
    expect(extractApiError(error)).toBe('bad request payload')
  })

  it('returns the raw axios message when no response body is attached', () => {
    const error = new AxiosError('timeout of 15000ms exceeded', 'ECONNABORTED')
    expect(extractApiError(error)).toBe('timeout of 15000ms exceeded')
  })

  it('returns a generic message for non-axios errors', () => {
    expect(extractApiError(new TypeError('boom'))).toBe('An unexpected error occurred.')
    expect(extractApiError(null)).toBe('An unexpected error occurred.')
  })
})
