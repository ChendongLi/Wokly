import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

const api = async (path, options = {}) => {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

export function useCurrentWeek() {
  return useQuery({
    queryKey: ['week', 'current'],
    queryFn: () => api('/api/week/current'),
  })
}

export function useTriggerGenerate() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => api('/api/generate', { method: 'POST' }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['week'] }),
  })
}

export function useUpdateMeal() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ mealId, dish_slot, dish }) =>
      api(`/api/meal/${mealId}`, {
        method: 'PUT',
        body: JSON.stringify({ dish_slot, dish }),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['week'] }),
  })
}

export function useFillDish() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ mealId, dish_slot, name, url }) =>
      api(`/api/meal/${mealId}/fill`, {
        method: 'POST',
        body: JSON.stringify({ dish_slot, name, url }),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['week'] }),
  })
}

export function useRegenDish() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ mealId, dish_slot }) =>
      api(`/api/meal/${mealId}/regen`, {
        method: 'POST',
        body: JSON.stringify({ dish_slot }),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['week'] }),
  })
}

export function useHistory() {
  return useQuery({
    queryKey: ['history'],
    queryFn: () => api('/api/history'),
  })
}

export function useWeekDetail(weekId) {
  return useQuery({
    queryKey: ['week', weekId],
    queryFn: () => api(`/api/week/${weekId}`),
    enabled: !!weekId,
  })
}

export function useIngredients() {
  return useQuery({
    queryKey: ['ingredients', 'current'],
    queryFn: () => api('/api/ingredients/current'),
  })
}

export function useUpdateIngredient() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...body }) =>
      api(`/api/ingredients/${id}`, {
        method: 'PUT',
        body: JSON.stringify(body),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['ingredients'] }),
  })
}

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => api('/api/health'),
    retry: false,
  })
}

export function useDeleteWeek() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (weekId) => api(`/api/week/${weekId}`, { method: 'DELETE' }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['week'] })
      qc.invalidateQueries({ queryKey: ['history'] })
      qc.invalidateQueries({ queryKey: ['ingredients'] })
    },
  })
}

export function useGetPrompt() {
  return useQuery({
    queryKey: ['prompt'],
    queryFn: () => api('/api/prompt'),
  })
}

export function useUpdatePrompt() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (content) =>
      api('/api/prompt', {
        method: 'PUT',
        body: JSON.stringify({ content }),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['prompt'] }),
  })
}

export function useResetPrompt() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => api('/api/prompt', { method: 'DELETE' }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['prompt'] }),
  })
}
