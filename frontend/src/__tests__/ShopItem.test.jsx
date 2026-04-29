import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import ShopItem from '../components/ShopItem'

const mutateMock = vi.fn()
vi.mock('../hooks/useMenu', () => ({
  useUpdateIngredient: () => ({ mutate: mutateMock }),
}))

function wrapper({ children }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return <QueryClientProvider client={qc}>{children}</QueryClientProvider>
}

const makeItem = (overrides = {}) => ({
  id: 'ing-1',
  name: '猪里脊',
  quantity: '500g',
  store: 'costco',
  checked: false,
  ...overrides,
})

describe('ShopItem', () => {
  beforeEach(() => mutateMock.mockClear())

  it('renders ingredient name', () => {
    render(<ShopItem item={makeItem()} />, { wrapper })
    expect(screen.getByText('猪里脊')).toBeTruthy()
  })

  it('renders quantity', () => {
    render(<ShopItem item={makeItem()} />, { wrapper })
    expect(screen.getByText('500g')).toBeTruthy()
  })

  it('renders store badge', () => {
    render(<ShopItem item={makeItem({ store: 'costco' })} />, { wrapper })
    expect(screen.getByText('Costco')).toBeTruthy()
  })

  it('renders T&T badge for tnt items', () => {
    render(<ShopItem item={makeItem({ store: 'tnt' })} />, { wrapper })
    expect(screen.getByText('T&T')).toBeTruthy()
  })

  it('calls mutate with checked=true when checkbox clicked', async () => {
    const user = userEvent.setup()
    render(<ShopItem item={makeItem({ checked: false })} />, { wrapper })
    // The checkbox is the first button
    const checkbox = screen.getAllByRole('button')[0]
    await user.click(checkbox)
    expect(mutateMock).toHaveBeenCalledWith({ id: 'ing-1', checked: true })
  })

  it('calls mutate with checked=false when already checked', async () => {
    const user = userEvent.setup()
    render(<ShopItem item={makeItem({ checked: true })} />, { wrapper })
    const checkbox = screen.getAllByRole('button')[0]
    await user.click(checkbox)
    expect(mutateMock).toHaveBeenCalledWith({ id: 'ing-1', checked: false })
  })

  it('swaps store from costco to tnt when store badge clicked', async () => {
    const user = userEvent.setup()
    render(<ShopItem item={makeItem({ store: 'costco' })} />, { wrapper })
    await user.click(screen.getByText('Costco'))
    expect(mutateMock).toHaveBeenCalledWith({ id: 'ing-1', store: 'tnt' })
  })

  it('swaps store from tnt to costco when store badge clicked', async () => {
    const user = userEvent.setup()
    render(<ShopItem item={makeItem({ store: 'tnt' })} />, { wrapper })
    await user.click(screen.getByText('T&T'))
    expect(mutateMock).toHaveBeenCalledWith({ id: 'ing-1', store: 'costco' })
  })

  it('applies strikethrough and opacity when checked', () => {
    render(<ShopItem item={makeItem({ checked: true })} />, { wrapper })
    const nameEl = screen.getByText('猪里脊')
    expect(nameEl.className).toContain('line-through')
  })

  it('shows checkmark when item is checked', () => {
    render(<ShopItem item={makeItem({ checked: true })} />, { wrapper })
    expect(screen.getByText('✓')).toBeTruthy()
  })
})
