import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import DishCard from '../components/DishCard'

const { mockRegenMutate, mockUpdateMutate, mockFillMutate } = vi.hoisted(() => ({
  mockRegenMutate: vi.fn(),
  mockUpdateMutate: vi.fn(),
  mockFillMutate: vi.fn(),
}))

vi.mock('../hooks/useMenu', () => ({
  useRegenDish: () => ({ mutate: mockRegenMutate, isPending: false }),
  useUpdateMeal: () => ({ mutate: mockUpdateMutate, isPending: false }),
  useFillDish: () => ({ mutate: mockFillMutate, isPending: false }),
}))

const mockDish = {
  name: '红烧鸡块',
  tag: 'meat',
  style: '炖烧',
  diff: 3,
  ingredients: '鸡腿、酱油',
  steps: ['焯水', '炒色', '炖煮'],
  search_query: '红烧鸡块做法',
}

function wrapper({ children }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return <QueryClientProvider client={qc}>{children}</QueryClientProvider>
}

describe('DishCard', () => {
  beforeEach(() => {
    mockRegenMutate.mockClear()
    mockUpdateMutate.mockClear()
    mockFillMutate.mockClear()
  })

  it('renders dish name', () => {
    render(<DishCard dish={mockDish} mealId="m1" slot="dish1" />, { wrapper })
    expect(screen.getByText('红烧鸡块')).toBeTruthy()
  })

  it('renders cooking style', () => {
    render(<DishCard dish={mockDish} mealId="m1" slot="dish1" />, { wrapper })
    expect(screen.getByText('炖烧')).toBeTruthy()
  })

  it('renders tag badge', () => {
    render(<DishCard dish={mockDish} mealId="m1" slot="dish1" />, { wrapper })
    expect(screen.getByText('荤')).toBeTruthy()
  })

  it('renders difficulty stars', () => {
    render(<DishCard dish={mockDish} mealId="m1" slot="dish1" />, { wrapper })
    expect(screen.getByText('⭐⭐⭐')).toBeTruthy()
  })

  it('renders regen and edit buttons when not readOnly', () => {
    render(<DishCard dish={mockDish} mealId="m1" slot="dish1" />, { wrapper })
    expect(screen.getByTitle('重新生成')).toBeTruthy()
    expect(screen.getByTitle('编辑')).toBeTruthy()
  })

  it('hides regen and edit buttons in readOnly mode', () => {
    render(<DishCard dish={mockDish} mealId="m1" slot="dish1" readOnly />, { wrapper })
    expect(screen.queryByTitle('重新生成')).toBeNull()
    expect(screen.queryByTitle('编辑')).toBeNull()
  })

  it('opens RecipeDrawer when card is clicked', async () => {
    const user = userEvent.setup()
    render(<DishCard dish={mockDish} mealId="m1" slot="dish1" />, { wrapper })
    const card = screen.getByText('红烧鸡块').closest('div')
    await user.click(card)
    expect(screen.getAllByText('红烧鸡块').length).toBeGreaterThan(1)
  })

  it('renders nothing when dish is null', () => {
    const { container } = render(<DishCard dish={null} mealId="m1" slot="dish1" />, { wrapper })
    expect(container.firstChild).toBeNull()
  })

  it('calls regen mutate when ↺ button clicked', async () => {
    const user = userEvent.setup()
    render(<DishCard dish={mockDish} mealId="m1" slot="dish1" />, { wrapper })
    await user.click(screen.getByTitle('重新生成'))
    expect(mockRegenMutate).toHaveBeenCalledWith({ mealId: 'm1', dish_slot: 'dish1' })
  })

  // ── inline edit ──────────────────────────────────────────────────────────────

  it('shows edit form with pre-filled name when ✎ is clicked', async () => {
    const user = userEvent.setup()
    render(<DishCard dish={mockDish} mealId="m1" slot="dish1" />, { wrapper })
    await user.click(screen.getByTitle('编辑'))
    const nameInput = screen.getByPlaceholderText('菜名')
    expect(nameInput).toBeTruthy()
    expect(nameInput.value).toBe('红烧鸡块')
    expect(screen.getByPlaceholderText('食谱链接（可选）')).toBeTruthy()
  })

  it('cancels edit and restores dish card view', async () => {
    const user = userEvent.setup()
    render(<DishCard dish={mockDish} mealId="m1" slot="dish1" />, { wrapper })
    await user.click(screen.getByTitle('编辑'))
    await user.click(screen.getByText('取消'))
    expect(screen.getByText('红烧鸡块')).toBeTruthy()
    expect(screen.queryByPlaceholderText('菜名')).toBeNull()
  })

  it('calls fillDish.mutate when dish name changes on save', async () => {
    mockFillMutate.mockImplementation((_data, opts) => opts?.onSuccess?.())
    const user = userEvent.setup()
    render(<DishCard dish={mockDish} mealId="m1" slot="dish1" />, { wrapper })
    await user.click(screen.getByTitle('编辑'))
    const nameInput = screen.getByPlaceholderText('菜名')
    await user.clear(nameInput)
    await user.type(nameInput, '新菜名')
    await user.click(screen.getByText('保存'))
    expect(mockFillMutate).toHaveBeenCalledWith(
      expect.objectContaining({ mealId: 'm1', dish_slot: 'dish1', name: '新菜名' }),
      expect.any(Object)
    )
    expect(mockUpdateMutate).not.toHaveBeenCalled()
  })

  it('calls updateMeal.mutate when only URL changes (name unchanged)', async () => {
    mockUpdateMutate.mockImplementation((_data, opts) => opts?.onSuccess?.())
    const user = userEvent.setup()
    render(<DishCard dish={mockDish} mealId="m1" slot="dish1" />, { wrapper })
    await user.click(screen.getByTitle('编辑'))
    await user.type(screen.getByPlaceholderText('食谱链接（可选）'), 'https://example.com')
    await user.click(screen.getByText('保存'))
    expect(mockUpdateMutate).toHaveBeenCalledWith(
      expect.objectContaining({ mealId: 'm1', dish_slot: 'dish1' }),
      expect.any(Object)
    )
    expect(mockFillMutate).not.toHaveBeenCalled()
  })

  it('includes custom URL in saved dish when provided', async () => {
    mockUpdateMutate.mockImplementation((_data, opts) => opts?.onSuccess?.())
    const user = userEvent.setup()
    render(<DishCard dish={mockDish} mealId="m1" slot="dish1" />, { wrapper })
    await user.click(screen.getByTitle('编辑'))
    await user.type(screen.getByPlaceholderText('食谱链接（可选）'), 'https://example.com/recipe')
    await user.click(screen.getByText('保存'))
    expect(mockUpdateMutate).toHaveBeenCalledWith(
      expect.objectContaining({
        dish: expect.objectContaining({ url: 'https://example.com/recipe' }),
      }),
      expect.any(Object)
    )
  })

  it('pre-fills existing dish.url in URL input', async () => {
    const user = userEvent.setup()
    const dishWithUrl = { ...mockDish, url: 'https://existing.com' }
    render(<DishCard dish={dishWithUrl} mealId="m1" slot="dish1" />, { wrapper })
    await user.click(screen.getByTitle('编辑'))
    expect(screen.getByPlaceholderText('食谱链接（可选）').value).toBe('https://existing.com')
  })
})
