import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register, SessionUsage } from 'claude-code'

import type { Progress, Usage, UsageLimit } from '../types'

const REFRESH_MS = 60_000
const CACHE_KEY = 'last-limits'

const PROGRESS_PROMPT = [
  '(btw) 지금까지의 진행상황을 짧게 알려줘.',
  '- 정확히 3줄로, 각 줄은 "완료: ", "진행: ", "남음: " 으로 시작한다.',
  '- 각 줄은 한 문장으로 짧게, 한국어 평어체(-한다, -했다)로 쓴다.',
  '- 도구는 쓰지 말고 지금까지의 대화 내용만으로 답한다.',
].join('\n')

const LINE_PREFIX = /^(완료|진행|남음)\s*[:：]\s*/
const LINE_COLORS: Record<string, string> = {
  완료: 'success',
  진행: 'suggestion',
  남음: 'warning',
}

const usage = atom({ plugin: 'usage-progress', key: 'usage' } as const, null)
const isPinned = atom({ plugin: 'usage-progress', key: 'isPinned' } as const, false)
const progress = atom({ plugin: 'usage-progress', key: 'progress' } as const, {
  status: 'idle',
  text: '',
})

const LIMIT_LABELS: Record<string, string> = {
  five_hour: '5h',
  seven_day: '7d',
  spend_limit: 'spend',
}

function toUsage(
  u: Pick<SessionUsage, 'context' | 'rateLimits' | 'cost'>,
): Usage {
  return {
    tokens: u.context.tokens,
    window: u.context.window,
    percent: u.context.percent,
    limits: u.rateLimits.map(l => ({
      kind: l.kind,
      percentUsed: l.percentUsed,
      resetsAt: l.resetsAt,
    })),
    costUsd: u.cost?.usd,
  }
}

function compact(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${Math.round(n / 1_000)}k`
  return String(n)
}

function timeLeft(resetsAt: string | undefined, now: number): string {
  if (resetsAt === undefined) return ''
  const ms = Date.parse(resetsAt) - now
  if (!(ms > 0)) return ''

  const total = Math.round(ms / 60_000)
  const days = Math.floor(total / 1_440)
  const hours = Math.floor((total % 1_440) / 60)
  const minutes = total % 60
  const parts = [`${minutes}m`]
  if (days > 0 || hours > 0) parts.unshift(`${hours}h`)
  if (days > 0) parts.unshift(`${days}d`)

  return ` (${parts.join(' ')})`
}

type Segment = { text: string; color?: string; isDim?: boolean }

const SEPARATOR: Segment = { text: ' | ', isDim: true }
const LIMIT_COLORS: Record<string, string> = {
  five_hour: 'suggestion',
  seven_day: 'permission',
  spend_limit: 'remember',
}

function severity(percent: number): string {
  if (percent >= 85) return 'error'
  if (percent >= 60) return 'warning'
  return 'success'
}

function remainingColor(left: number): string {
  if (left <= 15) return 'error'
  if (left <= 40) return 'warning'
  return 'success'
}

function segments(u: Usage | null, now: number): Segment[] {
  if (u === null) return [{ text: 'no usage data yet', isDim: true }]

  const groups: Segment[][] = []
  if (u.percent === undefined || u.tokens === undefined) {
    groups.push([
      { text: 'ctx ', color: 'claude' },
      { text: '첫 응답 후 표시', isDim: true },
    ])
  } else {
    groups.push([
      { text: 'ctx ', color: 'claude' },
      { text: `${u.percent}%`, color: severity(u.percent) },
      { text: ` ${compact(u.tokens)}/${compact(u.window)}`, isDim: true },
    ])
  }
  for (const limit of u.limits) {
    const label = LIMIT_LABELS[limit.kind] ?? limit.kind
    const left = Math.max(0, Math.round((100 - limit.percentUsed) * 10) / 10)
    const reset = timeLeft(limit.resetsAt, now)
    groups.push([
      { text: `${label} `, color: LIMIT_COLORS[limit.kind] ?? 'subtle' },
      { text: `${left}%`, color: remainingColor(left) },
      { text: ' left', isDim: true },
      ...(reset === '' ? [] : [{ text: reset, isDim: true }]),
    ])
  }
  if (u.isCached === true && u.limits.length > 0) {
    groups.push([{ text: 'cached', isDim: true }])
  }
  if (u.costUsd !== undefined && u.costUsd > 0) {
    groups.push([{ text: `$${u.costUsd.toFixed(2)}`, color: 'text' }])
  }

  return groups.flatMap((group, i) => (i === 0 ? group : [SEPARATOR, ...group]))
}

function parseLimits(value: unknown, now: number): UsageLimit[] {
  if (!Array.isArray(value)) return []

  return value.filter((item): item is UsageLimit => {
    if (typeof item !== 'object' || item === null) return false
    const limit = item as Partial<UsageLimit>
    if (typeof limit.kind !== 'string') return false
    if (typeof limit.percentUsed !== 'number') return false

    return typeof limit.resetsAt !== 'string' || Date.parse(limit.resetsAt) > now
  })
}

async function apply(
  $: EngineInterface,
  u: Pick<SessionUsage, 'context' | 'rateLimits' | 'cost'>,
): Promise<void> {
  const snapshot = toUsage(u)

  if (snapshot.limits.length > 0) {
    await $.store.set(CACHE_KEY, snapshot.limits).catch(() => undefined)
  } else {
    const now = await $.clock.now()
    const cached = parseLimits(await $.store.get(CACHE_KEY).catch(() => undefined), now)
    if (cached.length > 0) {
      snapshot.limits = cached
      snapshot.isCached = true
    }
  }

  await update($, usage, () => snapshot)
}

async function refresh($: EngineInterface): Promise<void> {
  await apply($, await $.session.usage())
}

async function askProgress($: EngineInterface): Promise<void> {
  const current = await read($, progress)
  if (current.status === 'loading') return

  await update($, progress, () => ({ status: 'loading', text: '' }))

  try {
    const r = await $.model.fork({ prompt: PROGRESS_PROMPT })
    if (r.isAnswered) {
      await update($, progress, () => ({ status: 'done', text: r.text.trim() }))
    } else if (r.reason === 'nothing-to-fork') {
      await update($, progress, () => ({
        status: 'done',
        text: '아직 진행한 작업이 없다.',
      }))
    } else {
      await update($, progress, () => ({
        status: 'error',
        text: `응답을 받지 못했다 (${r.reason})`,
      }))
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    await update($, progress, () => ({ status: 'error', text: message }))
  }
}

type Ui = ReturnType<EngineInterface['ui']['resolve']>

function detailView(ui: Ui, current: Usage | null, now: number) {
  const { Text } = ui

  return (
    <Text>
      {segments(current, now).map(seg => (
        <Text color={seg.color} dimColor={seg.isDim}>
          {seg.text}
        </Text>
      ))}
    </Text>
  )
}

function progressView($: EngineInterface, ui: Ui, ask: Progress, clearKey: string) {
  const { Box, Button, Text } = ui
  if (ask.status === 'idle') return null

  const lines = ask.text.split('\n').filter(line => line.trim() !== '')

  return (
    <Box gap={1}>
      {ask.status === 'done' ? (
        <Box flexDirection="column">
          {lines.map(line => {
            const match = LINE_PREFIX.exec(line)
            if (match === null) return <Text>{line}</Text>
            const tag = match[1] ?? ''

            return (
              <Text>
                <Text bold color={LINE_COLORS[tag]}>
                  {tag}
                </Text>
                <Text dimColor> | </Text>
                <Text>{line.slice(match[0].length)}</Text>
              </Text>
            )
          })}
        </Box>
      ) : (
        <Text
          dimColor={ask.status === 'loading'}
          color={ask.status === 'error' ? 'error' : undefined}
        >
          {ask.status === 'loading' ? '진행상황 확인 중...' : ask.text}
        </Text>
      )}
      {ask.status !== 'loading' && (
        <Button
          key={clearKey}
          label="닫기"
          plain
          dimColor
          onPress={() => update($, progress, () => ({ status: 'idle', text: '' }))}
        />
      )}
    </Box>
  )
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command
      .register({
        name: 'up',
        description: 'Show usage and a progress button in the transcript (any surface)',
      })
      .catch(() => undefined)
    await $.command
      .register({
        name: 'prog',
        description: 'Summarise the progress so far as a btw-style side question',
      })
      .catch(() => undefined)
    await refresh($).catch(() => undefined)
    $.clock.every(REFRESH_MS, () => {
      void refresh($).catch(() => undefined)
    })

    return next(e)
  })

  on('session.measure', async ($, e, next) => {
    await apply($, e).catch(() => undefined)

    return next(e)
  })

  on('command.run', { command: 'up' }, async $ => {
    await refresh($).catch(() => undefined)
    const current = await read($, usage)
    const now = await $.clock.now()

    return { text: segments(current, now).map(seg => seg.text).join('') }
  })

  on('command.run', { command: 'prog' }, async $ => {
    await askProgress($)
    const ask = await read($, progress)

    return { text: ask.text === '' ? '진행상황을 가져오지 못했다.' : ask.text }
  })

  on('ui.render', { component: 'CommandOutput', props: { command: 'up' } }, async ($, e) => {
    const ui = $.ui.resolve(e)
    const { Box, Button } = ui
    const current = await read($, usage)
    const ask = await read($, progress)
    const now = await $.clock.now()

    return (
      <Box flexDirection="column">
        <Box gap={1}>
          <Button key="o-progress" label="진행상황" onPress={() => askProgress($)} />
          <Button
            key="o-refresh"
            label="새로고침"
            onPress={() => refresh($).catch(() => undefined)}
          />
        </Box>
        {detailView(ui, current, now)}
        {progressView($, ui, ask, 'o-clear')}
      </Box>
    )
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey) {
      return next(e)
    }

    const ui = $.ui.resolve(e)
    const { Box, Button } = ui
    const current = await read($, usage)
    const pinned = await read($, isPinned)
    const ask = await read($, progress)
    const now = await $.clock.now()

    const toggle = async () => {
      await update($, isPinned, was => !was)
      await refresh($).catch(() => undefined)
    }

    const detail = detailView(ui, current, now)

    return (
      <Box flexDirection="column">
        <Box gap={1}>
          <Button key="progress" label="진행상황" onPress={() => askProgress($)} />
          <Box key="usage-peek" gap={1}>
            <Button
              key="usage"
              label={pinned ? 'Usage (pinned)' : 'Usage'}
              hover={{ bold: true }}
              onPress={toggle}
            />
            {pinned ? (
              <Box>{detail}</Box>
            ) : (
              <Box display="none" hover={{ display: 'flex' }}>
                {detail}
              </Box>
            )}
          </Box>
        </Box>
        {progressView($, ui, ask, 'clear')}
      </Box>
    )
  })
}
