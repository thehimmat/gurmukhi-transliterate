// Romanize Gurmukhi lines with each scheme's own code, for tools/build_gold.py.
// Usage: node gold_romanize.cjs <node_modules dir>  < lines.json  > out.json
// Input: [{id, gurmukhi}]; output adds gurbaniakhar, banidb, banidb_ipa, shabados.
const path = require('path');
const dir = process.argv[2];
const anvaad = require(path.join(dir, 'anvaad-js'));       // MIT, Khalis Foundation (BaniDB)
const gutils = require(path.join(dir, 'gurmukhi-utils'));  // GPL-3.0, Shabad OS — run only
const lines = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = lines.map(({ id, gurmukhi }) => {
  const ascii = anvaad.unicode(gurmukhi, true);
  return {
    id,
    gurmukhi,
    gurbaniakhar: ascii,
    banidb: anvaad.translit(ascii),
    banidb_ipa: anvaad.translit(ascii, 'ipa'),
    shabados: gutils.toEnglish(gurmukhi),
  };
});
process.stdout.write(JSON.stringify(out));
