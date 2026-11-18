// Presentations-skill finalizer wrapper (validation + chart workbooks) so every build does not rewrite it.
// usage (run beside a node_modules link to the Codex runtime, with its node):
//   node finalize.mjs --draft /abs/draft.pptx --final /abs/FINAL.pptx --slides 9 --workspace /abs/round-dir \
//        [--tables 4,7] [--charts 3,5] [--family Pretendard] [--keep-workbooks] [--pair-ea "Apple SD Gothic Neo"] [--overwrite]
// The draft must live inside --workspace. Charts: materializeLiteralChartWorkbooks is on by default; without an embedded workbook Apple's renderer (QuickLook/Keynote preview) draws no chart.
import fs from 'node:fs/promises';
import {existsSync, readdirSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {pathToFileURL, fileURLToPath} from 'node:url';

const HOME = os.homedir();
process.env.RUNTIME_NODE_MODULES ??= path.join(HOME, '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules');

export function resolvePresentationsSkillDir() {
  if (process.env.PRESENTATIONS_SKILL_DIR) {
    if (existsSync(path.join(process.env.PRESENTATIONS_SKILL_DIR, 'container_tools/artifact_tool_utils.mjs'))) {
      return process.env.PRESENTATIONS_SKILL_DIR;
    }
    throw new Error(`PRESENTATIONS_SKILL_DIR lacks container_tools/artifact_tool_utils.mjs: ${process.env.PRESENTATIONS_SKILL_DIR}`);
  }
  const cacheBase = path.join(HOME, '.codex/plugins/cache/openai-primary-runtime/presentations');
  if (existsSync(cacheBase)) {
    const versions = readdirSync(cacheBase, {withFileTypes: true})
      .filter(d => d.isDirectory())
      .map(d => d.name)
      .sort((x, y) => x.localeCompare(y, undefined, {numeric: true}));
    for (let i = versions.length - 1; i >= 0; i--) {
      const candidate = path.join(cacheBase, versions[i], 'skills/presentations');
      if (existsSync(path.join(candidate, 'container_tools/artifact_tool_utils.mjs'))) return candidate;
    }
  }
  throw new Error(
    `Codex presentations runtime skill not found under ${cacheBase}. Set PRESENTATIONS_SKILL_DIR to the presentations skill directory.`,
  );
}

const codexPy = path.join(HOME, '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3');
export const PY = process.env.RUNTIME_PYTHON || (existsSync(codexPy) ? codexPy : 'python3');
export const SKILL_DIR = resolvePresentationsSkillDir();
export const {finalizePresentation} = await import(pathToFileURL(path.join(SKILL_DIR, 'container_tools/artifact_tool_utils.mjs')).href);

function findSkillRoot(relScript) {
  const here = path.dirname(fileURLToPath(import.meta.url));
  return [
    process.env.RESEARCH_DECK_SKILL,
    process.env.RESEARCH_TALK_SKILL,
    path.resolve(here, '..', '..'),
    path.join(HOME, '.codex/skills/html-research-deck'),
  ]
    .filter(Boolean)
    .find(r => existsSync(path.join(r, relScript)));
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const a = Object.fromEntries(
    process.argv.slice(2).reduce(
      (acc, v, i, arr) => (v.startsWith('--') ? [...acc, [v.slice(2), arr[i + 1] && !arr[i + 1].startsWith('--') ? arr[i + 1] : true]] : acc),
      [],
    ),
  );
  if (a.help || !a.draft || !a.final || !a.workspace) {
    console.log('usage: node finalize.mjs --draft /abs/draft.pptx --final /abs/FINAL.pptx --slides N --workspace /abs/dir [...]');
    process.exit(a.help ? 0 : 2);
  }
  const list = s => (s && s !== true ? String(s).split(',').map(Number) : []);
  const tables = list(a.tables), charts = list(a.charts);
  let draftPath = a.draft;
  const families = [a.family && a.family !== true ? a.family : 'Pretendard'];
  if (a['pair-ea'] && a['pair-ea'] !== true) {
    const {execFileSync} = await import('node:child_process');
    draftPath = a.draft.replace(/\.pptx$/, '.paired.pptx');
    const skillRoot = findSkillRoot('scripts/pptx/pair_fonts.py');
    if (!skillRoot) throw new Error('pair_fonts.py not found: set RESEARCH_DECK_SKILL to the html-research-deck skill folder');
    execFileSync(PY, [path.join(skillRoot, 'scripts/pptx/pair_fonts.py'), a.draft, draftPath, families[0], a['pair-ea']], {stdio: 'inherit'});
    families.push(a['pair-ea']);
  }
  if (families[0] === 'Pretendard') {
    const {spawnSync} = await import('node:child_process');
    const rootF = findSkillRoot('scripts/pptx/ensure_font.py');
    if (rootF) {
      const r = spawnSync(PY, [path.join(rootF, 'scripts/pptx/ensure_font.py')], {encoding: 'utf8'});
      console.log((r.stdout || '').trim() || (r.stderr || '').trim());
    }
  }
  {
    const {execFileSync} = await import('node:child_process');
    const root2 = findSkillRoot('scripts/pptx/set_theme_fonts.py');
    if (root2) {
      const themed = draftPath.replace(/\.pptx$/, '.themed.pptx');
      execFileSync(PY, [path.join(root2, 'scripts/pptx/set_theme_fonts.py'), draftPath, themed, families[0], families[1] ?? families[0]], {stdio: 'inherit'});
      draftPath = themed;
      if (existsSync(path.join(root2, 'scripts/pptx/chart_no_autotitle.py'))) {
        const notitle = draftPath.replace(/\.themed\.pptx$/, '.notitle.pptx');
        execFileSync(PY, [path.join(root2, 'scripts/pptx/chart_no_autotitle.py'), draftPath, notitle], {stdio: 'inherit'});
        draftPath = notitle;
      }
    }
  }
  const staging = path.join(a.workspace, '.codex-finalizer');
  await fs.mkdir(staging, {recursive: true});
  await fs.rm(path.join(staging, path.basename(a.final) + '.validation.json'), {force: true});
  if (a.overwrite) await fs.rm(a.final, {force: true});
  await fs.mkdir(path.dirname(a.final), {recursive: true});
  const result = await finalizePresentation({
    explicitTotalSlideCount: Number(a.slides),
    requiredNativeTableOwnerSlides: tables,
    requiredNativeChartOwnerSlides: charts,
    materializeLiteralChartWorkbooks: !a['keep-workbooks'],
    workspaceDir: a.workspace,
    candidatePath: draftPath,
    finalPath: a.final,
    pythonExecutable: PY,
    integrityValidatorPath: path.join(SKILL_DIR, 'container_tools/inspect_presentation_package_integrity.py'),
    layoutValidatorPath: path.join(SKILL_DIR, 'container_tools/inspect_presentation_layout_geometry.py'),
    layoutArgs: [
      '--expected-slide-size-emu',
      '24384000,13716000',
      '--validate-bullet-geometry',
      '--validate-heading-fit',
      ...tables.flatMap(n => ['--require-native-table-slide', String(n)]),
    ],
    fontPolicy: {basis: 'design', families},
    verifyArtifactToolImport: true,
    receiptPath: path.join(staging, path.basename(a.final) + '.validation.json'),
  });
  console.log(JSON.stringify(result, null, 1).slice(0, 4000));
}
