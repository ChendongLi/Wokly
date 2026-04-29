import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import DayNav from '../components/DayNav'

describe('DayNav', () => {
  it('renders all 5 day pills', () => {
    render(<DayNav selected="周一" onChange={() => {}} />)
    for (const day of ['周一', '周二', '周三', '周四', '周五']) {
      expect(screen.getByText(day)).toBeTruthy()
    }
  })

  it('highlights the selected day', () => {
    render(<DayNav selected="周三" onChange={() => {}} />)
    const btn = screen.getByText('周三')
    expect(btn.className).toContain('bg-orange-500')
  })

  it('does not highlight unselected days', () => {
    render(<DayNav selected="周三" onChange={() => {}} />)
    const btn = screen.getByText('周一')
    expect(btn.className).not.toContain('bg-orange-500')
  })

  it('calls onChange with the clicked day', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    render(<DayNav selected="周一" onChange={onChange} />)
    await user.click(screen.getByText('周五'))
    expect(onChange).toHaveBeenCalledWith('周五')
    expect(onChange).toHaveBeenCalledTimes(1)
  })
})
