import api, { unwrap } from '@/api/client'
import type { DeliveryFileRecord } from '@/types/domain'

export const deliveriesApi = {
  list(packageId: string) {
    return unwrap<DeliveryFileRecord[]>(api.get(`/deliveries/${packageId}`))
  },
  createLink(packageId: string, payload: Record<string, unknown>) {
    return unwrap<{ token: string; expires_at: string; delivery_file_id: string }>(api.post(`/deliveries/${packageId}/links`, payload))
  },
  uploadFile(packageId: string, payload: { upload: File; file_type: string; is_final: boolean; allowed_roles: string[] }) {
    const formData = new FormData()
    formData.append('upload', payload.upload)
    formData.append('file_type', payload.file_type)
    formData.append('is_final', String(payload.is_final))
    payload.allowed_roles.forEach((role) => formData.append('allowed_roles', role))
    return unwrap<DeliveryFileRecord>(api.post(`/deliveries/${packageId}/files`, formData))
  },
  bulkDownload(packageId: string) {
    return unwrap<{ token: string; delivery_file_id: string; expires_at: string }>(api.post(`/deliveries/${packageId}/bulk-download`))
  },
  accept(packageId: string, payload: Record<string, unknown>) {
    return unwrap(api.post(`/deliveries/${packageId}/acceptance`, payload))
  },
  acceptance(packageId: string) {
    return unwrap<any[]>(api.get(`/deliveries/${packageId}/acceptance`))
  },
  async downloadByToken(token: string, bearerToken: string) {
    const response = await api.get(`/downloads/${token}`, {
      responseType: 'blob',
      headers: { Authorization: `Bearer ${bearerToken}` },
    })
    return response
  },
}
