import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import MenuTab from '../components/MenuTab'

const { generateMock } = vi.hoisted(() => ({ generateMock: vi.fn() }))

vi.mock('../hooks/useMenu', () => ({
  useCurrentWeek: vi.fn(),
  useTriggerGenerate: () => ({ mutate: generateMock, isPending: false, data: undefined }),
  useRegenDish: () => ({ mutate: vi.fn(), isPending: false }),
  useUpdateMeal: () => ({ mutate: vi.fn(), isPending: false }),
  useFillDish: () => ({ mutate: vi.fn(), isPending: false }),
  useWeekDetail: vi.fn(() => ({ data: undefined })),
}))

import { useCurrentWeek, useWeekDetail } from '../hooks/useMenu'

function wrapper({ children }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return <QueryClientProvider client={qc}>{children}</QueryClientProvider>
}

const makeMeal = (day, mealType) => ({
  id: `${day}-${mealType}`,
  day,
  meal_type: mealType,
  dish1: {
    name: `${day}${mealType}荤菜`,
    tag: 'meat',
    style: '快炒',
    diff: 2,
    ingredients: '猪肉',
    steps: ['step1'],
    search_query: 'test',
  },
  dish2: {
    name: `${day}${mealType}素菜`,
    tag: 'veg',
    style: '快炒',
    diff: 1,
    ingredients: '白菜',
    steps: ['step1'],
    search_query: 'test',
  },
  optional_dish: {
    name: `${day}凉拌`,
    tag: 'opt',
    style: '凉拌',
    diff: 1,
    ingredients: '黄瓜',
    steps: ['step1'],
    search_query: 'test',
  },
  soup: {
    name: `${day}汤`,
    tag: 'soup',
    style: '汤',
    diff: 1,
    ingredients: '番茄',
    steps: ['step1'],
    search_query: 'test',
  },
})

const mockWeek = {
  id: 'week-1',
  week_start: '2026-04-28',
  status: 'ready',
  meals: ['周一', '周二', '周三', '周四', '周五'].flatMap((day) => [
    makeMeal(day, 'lunch'),
    makeMeal(day, 'dinner'),
  ]),
}

beforeEach(() => generateMock.mockClear())

describe('MenuTab – empty state', () => {
  it('shows empty state message when no week data', () => {
    useCurrentWeek.mockReturnValue({ data: null, isLoading: false })
    render(<MenuTab />, { wrapper })
    expect(screen.getByText(/还没生成/)).toBeTruthy()
  })

  it('shows loading state', () => {
    useCurrentWeek.mockReturnValue({ data: null, isLoading: true })
    render(<MenuTab />, { wrapper })
    expect(screen.getByText('加载中…')).toBeTruthy()
  })

  it('shows generate button in empty state', () => {
    useCurrentWeek.mockReturnValue({ data: null, isLoading: false })
    render(<MenuTab />, { wrapper })
    // There are two generate buttons: header + empty state CTA
    const btns = screen.getAllByText('立即生成')
    expect(btns.length).toBeGreaterThan(0)
  })
})

describe('MenuTab – loaded state', () => {
  beforeEach(() => {
    useCurrentWeek.mockReturnValue({ data: mockWeek, isLoading: false })
  })

  it('renders day navigation', () => {
    render(<MenuTab />, { wrapper })
    for (const day of ['周一', '周二', '周三', '周四', '周五']) {
      expect(screen.getByText(day)).toBeTruthy()
    }
  })

  it('renders 周一 dishes by default', () => {
    render(<MenuTab />, { wrapper })
    expect(screen.getByText('周一lunch荤菜')).toBeTruthy()
    expect(screen.getByText('周一lunch素菜')).toBeTruthy()
    expect(screen.getByText('周一dinner荤菜')).toBeTruthy()
  })

  it('switches to 周三 dishes when that pill is clicked', async () => {
    const user = userEvent.setup()
    render(<MenuTab />, { wrapper })
    await user.click(screen.getByText('周三'))
    expect(screen.getByText('周三lunch荤菜')).toBeTruthy()
    expect(screen.queryByText('周一lunch荤菜')).toBeNull()
  })

  it('shows WFH toggle on lunch section', () => {
    render(<MenuTab />, { wrapper })
    expect(screen.getByText('太太在家')).toBeTruthy()
  })

  it('optional dish is hidden by default (WFH toggle off)', () => {
    render(<MenuTab />, { wrapper })
    expect(screen.queryByText('周一凉拌')).toBeNull()
  })

  it('optional dish appears when WFH toggle is switched on', async () => {
    const user = userEvent.setup()
    render(<MenuTab />, { wrapper })
    const toggle = screen.getByText('太太在家').closest('label').querySelector('div')
    await user.click(toggle)
    expect(screen.getByText('周一凉拌')).toBeTruthy()
  })

  it('shows soup in dinner section', () => {
    render(<MenuTab />, { wrapper })
    expect(screen.getByText('周一汤')).toBeTruthy()
  })

  it('calls generate mutate when header button clicked', async () => {
    const user = userEvent.setup()
    render(<MenuTab />, { wrapper })
    const btn = screen.getByText('生成菜单')
    await user.click(btn)
    expect(generateMock).toHaveBeenCalled()
  })
})

describe('MenuTab – readOnly mode', () => {
  it('hides generate button in readOnly mode', () => {
    useCurrentWeek.mockReturnValue({ data: mockWeek, isLoading: false })
    render(<MenuTab weekData={mockWeek} readOnly />, { wrapper })
    expect(screen.queryByText('生成菜单')).toBeNull()
  })
})

describe('MenuTab – generate navigates to referenced week', () => {
  it('shows 下周菜单 and 返回本周 when generated week differs from current', async () => {
    const nextWeek = { ...mockWeek, id: 'week-next', week_start: '2026-05-04' }
    useCurrentWeek.mockReturnValue({ data: mockWeek, isLoading: false })
    // After generate triggers onSuccess, MenuTab calls useWeekDetail('week-next') → nextWeek
    useWeekDetail.mockReturnValue({ data: nextWeek })
    generateMock.mockImplementation((_opts, callbacks) => {
      callbacks?.onSuccess?.({ week_id: 'week-next' })
    })

    const user = userEvent.setup()
    render(<MenuTab />, { wrapper })
    await user.click(screen.getByText('生成菜单'))

    expect(screen.getByText('下周菜单')).toBeTruthy()
    expect(screen.getByText('← 返回本周')).toBeTruthy()
  })
})
