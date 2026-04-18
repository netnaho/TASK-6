import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { NTag } from 'naive-ui'

import StatusBadge from './StatusBadge.vue'

function tagTypeOf(status: string): unknown {
  const wrapper = mount(StatusBadge, { props: { status } })
  const tag = wrapper.findComponent(NTag)
  expect(tag.exists()).toBe(true)
  return tag.props('type')
}

describe('StatusBadge', () => {
  it('renders the status label with underscores replaced by spaces', () => {
    const wrapper = mount(StatusBadge, { props: { status: 'in_review' } })
    expect(wrapper.text()).toContain('in review')
  })

  it('maps submitted/active/completed to the success tag type', () => {
    for (const status of ['submitted', 'active', 'completed']) {
      expect(tagTypeOf(status)).toBe('success')
    }
  })

  it('maps corrected/warning/queued to the warning tag type', () => {
    for (const status of ['corrected', 'warning', 'queued']) {
      expect(tagTypeOf(status)).toBe('warning')
    }
  })

  it('maps voided/withdrawn/disabled to the error tag type', () => {
    for (const status of ['voided', 'withdrawn', 'disabled']) {
      expect(tagTypeOf(status)).toBe('error')
    }
  })

  it('falls back to the info tag type for unknown statuses', () => {
    expect(tagTypeOf('something_else')).toBe('info')
    const wrapper = mount(StatusBadge, { props: { status: 'something_else' } })
    expect(wrapper.text()).toContain('something else')
  })
})
