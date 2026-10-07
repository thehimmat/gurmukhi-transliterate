const fs = require('fs');
const S = process.argv[2];
const grab = (file, name) => {
  const src = fs.readFileSync(`${S}/${file}`, 'utf8');
  const start = src.indexOf(`const ${name} = `);
  if (start < 0) throw new Error(`${name} not in ${file}`);
  let i = src.indexOf('=', start) + 1, depth = 0, inStr = null, j = i;
  for (; j < src.length; j++) {
    const ch = src[j];
    if (inStr) { if (ch === '\\') { j++; continue; } if (ch === inStr) inStr = null; continue; }
    if (ch === "'" || ch === '"' || ch === '`') { inStr = ch; continue; }
    if (ch === '[' || ch === '{' || ch === '(') depth++;
    if (ch === ']' || ch === '}' || ch === ')') depth--;
    if (ch === ';' && depth === 0) break;
  }
  return eval('(' + src.slice(i, j) + ')');
};
const out = {
  english_step1: grab('translit_modules/english.js', 'step1'),
  english_step2: grab('translit_modules/english.js', 'step2').map(([k, v]) => [String(k), v, typeof k]),
  english_step4: grab('translit_modules/english.js', 'step4'),
  ipa_step2: grab('translit_modules/ipa.js', 'step2'),
  ipa_charset: grab('translit_modules/ipa.js', 'ourCharset'),
  mapping: grab('unicode.js', 'mapping'),
  reverseMapping: grab('unicode.js', 'reverseMapping'),
  halfChars: grab('unicode.js', 'halfChars'),
  aboveChars: grab('unicode.js', 'aboveChars'),
  supplementaryChars: grab('unicode.js', 'supplementaryChars'),
  supplementaryCharMapping: grab('unicode.js', 'supplementaryCharMapping'),
};
// reverseMapping key order matters for duplicate PUA keys; Object keeps insertion order (last wins)
process.stdout.write(JSON.stringify(out));
