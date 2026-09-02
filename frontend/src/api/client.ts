const OPTS: RequestInit = { credentials: 'include' }

export const api = {
  get: (path: string) => fetch(path, OPTS),

  post: (path: string, body: unknown) =>
    fetch(path, {
      ...OPTS,
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),

  postForm: (path: string, form: FormData) =>
    fetch(path, { ...OPTS, method: 'POST', body: form }),

  delete: (path: string) => fetch(path, { ...OPTS, method: 'DELETE' }),
}

export async function parseErrorDetail(res: Response): Promise<string> {
  try {
    const json = await res.json()
    return json.detail ?? res.statusText
  } catch {
    return res.statusText
  }
}
