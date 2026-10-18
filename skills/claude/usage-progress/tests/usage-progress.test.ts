import { describe, expect, mock, test } from 'claude-code/testing'

const SURFACES = ['terminal', 'desktop'] as const

const BAND_PROPS = {
  hasSurvey: false,
  isWorking: false,
  maxRows: 10,
  bodyColumns: 100,
  scroll: { offset: 0, bodyRows: 10 },
  view: {},
}

const USAGE = {
  startedAt: 0,
  context: { tokens: 68_000, window: 200_000, percent: 34 },
  rateLimits: [
    { kind: 'five_hour', percentUsed: 23.5 },
    { kind: 'seven_day', percentUsed: 7 },
  ],
  cost: { usd: 1.234 },
}

const minutesFromNow = (m: number): string => new Date(m * 60_000).toISOString()

describe('usage-progress band', () => {
  for (const surface of SURFACES) {
    test(`shows both buttons and the usage detail on ${surface}`, async ($, on) => {
      mock.clock(on)
      on('session.start', () => ({ cwd: '/tmp' }))
    on('command.register', () => ({ value: { command: 'up' } }))
      on('session.usage', () => ({ value: USAGE }))

      const ui = await $.ui.mount({
        plugin: 'usage-progress',
        surface,
        component: 'AbovePrompt',
        props: BAND_PROPS,
      })
      await $.session.start({ cwd: '/tmp', surface, isInteractive: true })

      expect(await ui.find({ key: 'progress' })).toBeDefined()
      expect(await ui.find({ key: 'usage' })).toBeDefined()
      const detail = await ui.find({ type: 'Text', text: /ctx 34%/ })
      expect(detail?.text).toContain('68k/200k')
      expect(detail?.text).toContain('5h 76.5% left')
      expect(detail?.text).toContain('7d 93% left')
      expect(detail?.text).toContain('$1.23')

      await ui.unmount()
    })

    test(`usage button toggles the pin on ${surface}`, async ($, on) => {
      mock.clock(on)
      on('session.start', () => ({ cwd: '/tmp' }))
    on('command.register', () => ({ value: { command: 'up' } }))
      on('session.usage', () => ({ value: USAGE }))

      const ui = await $.ui.mount({
        plugin: 'usage-progress',
        surface,
        component: 'AbovePrompt',
        props: BAND_PROPS,
      })
      expect((await ui.find({ key: 'usage' }))?.text).toBe('Usage')

      await ui.press({ key: 'usage' })
      expect((await ui.find({ key: 'usage' }))?.text).toBe('Usage (pinned)')

      await ui.press({ key: 'usage' })
      expect((await ui.find({ key: 'usage' }))?.text).toBe('Usage')

      await ui.unmount()
    })

    test(`progress button shows the fork reply on ${surface}`, async ($, on) => {
      mock.clock(on)
      on('session.start', () => ({ cwd: '/tmp' }))
    on('command.register', () => ({ value: { command: 'up' } }))
      on('session.usage', () => ({ value: USAGE }))
      on('model.fork', () => ({
        value: {
          isAnswered: true,
          text: '완료: A\n진행: B\n남음: C',
          usage: {
            input_tokens: 1,
            output_tokens: 1,
            cache_read_input_tokens: 0,
            cache_creation_input_tokens: 0,
          },
        },
      }))

      const ui = await $.ui.mount({
        plugin: 'usage-progress',
        surface,
        component: 'AbovePrompt',
        props: BAND_PROPS,
      })
      await ui.press({ key: 'progress' })

      expect(await ui.find({ type: 'Text', text: /진행.*B/ })).toBeDefined()
      expect(await ui.find({ type: 'Text', text: /남음.*C/ })).toBeDefined()

      await ui.press({ key: 'clear' })
      expect(await ui.find({ type: 'Text', text: /진행.*B/ })).toBeUndefined()

      await ui.unmount()
    })

    test(`progress says so when there is nothing to fork on ${surface}`, async ($, on) => {
      mock.clock(on)
      on('session.start', () => ({ cwd: '/tmp' }))
    on('command.register', () => ({ value: { command: 'up' } }))
      on('session.usage', () => ({ value: USAGE }))
      on('model.fork', () => ({
        value: { isAnswered: false, reason: 'nothing-to-fork' },
      }))

      const ui = await $.ui.mount({
        plugin: 'usage-progress',
        surface,
        component: 'AbovePrompt',
        props: BAND_PROPS,
      })
      await ui.press({ key: 'progress' })

      expect(await ui.find({ type: 'Text', text: /아직 진행한 작업이 없다/ })).toBeDefined()

      await ui.unmount()
    })
  }
  test('reset times read as Nd Nh Nm', async ($, on) => {
    mock.clock(on)
    on('session.start', () => ({ cwd: '/tmp' }))
    on('command.register', () => ({ value: { command: 'up' } }))
    on('session.usage', () => ({
      value: {
        ...USAGE,
        rateLimits: [
          { kind: 'five_hour', percentUsed: 10, resetsAt: minutesFromNow(130) },
          { kind: 'seven_day', percentUsed: 20, resetsAt: minutesFromNow(9_365) },
          { kind: 'spend_limit', percentUsed: 30, resetsAt: minutesFromNow(45) },
        ],
      },
    }))

    const ui = await $.ui.mount({
      plugin: 'usage-progress',
      surface: 'desktop',
      component: 'AbovePrompt',
      props: BAND_PROPS,
    })
    await $.session.start({ cwd: '/tmp', surface: 'desktop', isInteractive: true })

    const detail = await ui.find({ type: 'Text', text: /ctx 34%/ })
    expect(detail?.text).toContain('5h 90% left (2h 10m)')
    expect(detail?.text).toContain('7d 80% left (6d 12h 5m)')
    expect(detail?.text).toContain('spend 70% left (45m)')

    await ui.unmount()
  })
  test('falls back to the last known limits and marks them cached', async ($, on) => {
    mock.clock(on)
    mock.store(on, {
      'last-limits': [
        { kind: 'five_hour', percentUsed: 40, resetsAt: minutesFromNow(100) },
        { kind: 'seven_day', percentUsed: 10, resetsAt: minutesFromNow(-5) },
      ],
    })
    on('session.start', () => ({ cwd: '/tmp' }))
    on('command.register', () => ({ value: { command: 'up' } }))
    on('session.usage', () => ({ value: { ...USAGE, rateLimits: [] } }))

    const ui = await $.ui.mount({
      plugin: 'usage-progress',
      surface: 'desktop',
      component: 'AbovePrompt',
      props: BAND_PROPS,
    })
    await $.session.start({ cwd: '/tmp', surface: 'desktop', isInteractive: true })

    const detail = await ui.find({ type: 'Text', text: /ctx 34%/ })
    expect(detail?.text).toContain('5h 60% left (1h 40m)')
    expect(detail?.text).toContain('cached')
    expect(detail?.text).not.toContain('7d')

    await ui.unmount()
  })

  test('says so before the first response when nothing is known', async ($, on) => {
    mock.clock(on)
    mock.store(on)
    on('session.start', () => ({ cwd: '/tmp' }))
    on('command.register', () => ({ value: { command: 'up' } }))
    on('session.usage', () => ({
      value: { startedAt: 0, context: { window: 200_000 }, rateLimits: [] },
    }))

    const ui = await $.ui.mount({
      plugin: 'usage-progress',
      surface: 'desktop',
      component: 'AbovePrompt',
      props: BAND_PROPS,
    })
    await $.session.start({ cwd: '/tmp', surface: 'desktop', isInteractive: true })

    expect(await ui.find({ type: 'Text', text: /첫 응답 후 표시/ })).toBeDefined()

    await ui.unmount()
  })
  for (const surface of ['terminal', 'desktop', 'vscode', 'mobile'] as const) {
    test(`the /up row draws and works on ${surface}`, async ($, on) => {
      mock.clock(on)
      mock.store(on)
      on('session.start', () => ({ cwd: '/tmp' }))
      on('command.register', () => ({ value: { command: 'up' } }))
      on('session.usage', () => ({ value: USAGE }))
      on('model.fork', () => ({
        value: {
          isAnswered: true,
          text: '완료: A\n진행: B\n남음: C',
          usage: {
            input_tokens: 1,
            output_tokens: 1,
            cache_read_input_tokens: 0,
            cache_creation_input_tokens: 0,
          },
        },
      }))

      const ui = await $.ui.mount({
        plugin: 'usage-progress',
        surface,
        component: 'CommandOutput',
        props: { command: 'up', args: '', text: 'x', isErrored: false },
      })
      await $.session.start({ cwd: '/tmp', surface, isInteractive: true })

      const detail = await ui.find({ type: 'Text', text: /ctx 34%/ })
      expect(detail?.text).toContain('5h 76.5% left')

      await ui.press({ key: 'o-progress' })
      expect(await ui.find({ type: 'Text', text: /진행.*B/ })).toBeDefined()

      await ui.press({ key: 'o-clear' })
      expect(await ui.find({ type: 'Text', text: /진행.*B/ })).toBeUndefined()

      await ui.unmount()
    })
  }

  test('/up prints the usage as plain text', async ($, on) => {
    mock.clock(on)
    mock.store(on)
    on('session.usage', () => ({ value: USAGE }))

    const ran = await $.command.run({
      command: 'up',
      args: '',
      origin: { kind: 'composer' },
      presentation: { isFullscreen: false, columns: 80 },
    })

    expect(JSON.stringify(ran)).toContain('5h 76.5% left')
  })

  test('/prog prints the fork summary', async ($, on) => {
    mock.clock(on)
    mock.store(on)
    on('session.usage', () => ({ value: USAGE }))
    on('model.fork', () => ({
      value: {
        isAnswered: true,
        text: '완료: A\n진행: B\n남음: C',
        usage: {
          input_tokens: 1,
          output_tokens: 1,
          cache_read_input_tokens: 0,
          cache_creation_input_tokens: 0,
        },
      },
    }))

    const ran = await $.command.run({
      command: 'prog',
      args: '',
      origin: { kind: 'composer' },
      presentation: { isFullscreen: false, columns: 80 },
    })

    expect(JSON.stringify(ran)).toContain('진행: B')
  })
})
