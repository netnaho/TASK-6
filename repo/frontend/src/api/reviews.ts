import api, { unwrap } from '@/api/client'
import type { ReviewContext } from '@/types/domain'

export const reviewsApi = {
  queue() {
    return unwrap<any[]>(api.get('/reviews/queue'))
  },
  context(packageId: string) {
    return unwrap<ReviewContext>(api.get(`/reviews/${packageId}/context`))
  },
  corrections(packageId: string) {
    return unwrap<any[]>(api.get(`/reviews/${packageId}/corrections`))
  },
  requestCorrection(packageId: string, payload: Record<string, unknown>) {
    return unwrap(api.post(`/reviews/${packageId}/request-correction`, payload))
  },
  complete(packageId: string, payload: Record<string, unknown>) {
    return unwrap(api.post(`/reviews/${packageId}/complete`, payload))
  },
}
