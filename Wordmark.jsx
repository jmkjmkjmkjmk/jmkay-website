// Wordmark.jsx — the J.M.KAY mark at any scale, with diamond dots.
// Sizes are tuned to the BRAND-SYSTEM.md per-scale specs.

const WORDMARK_SIZES = {
  hero:     { fs: 72, dot: 14, mx: 5 },
  display:  { fs: 56, dot: 11, mx: 4 },
  section:  { fs: 40, dot: 8,  mx: 3 },
  nav:      { fs: 20, dot: 6,  mx: 2 },
  footer:   { fs: 40, dot: 8,  mx: 3 },
};

function Wordmark({ size = 'hero', onDark = false, as = 'div' }) {
  const { fs, dot, mx } = WORDMARK_SIZES[size] || WORDMARK_SIZES.hero;
  const Tag = as;
  return (
    <Tag
      className="t-wordmark"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        fontFamily: 'var(--font-display)',
        fontWeight: 400,
        fontSize: fs,
        letterSpacing: '0.05em',
        lineHeight: 1,
        color: onDark ? 'var(--warm-white)' : 'var(--ink)',
      }}
      aria-label="J.M.Kay"
    >
      J
      <span className="jmk-d" aria-hidden="true"
        style={{ width: dot, height: dot, margin: `0 ${mx}px` }} />
      M
      <span className="jmk-d" aria-hidden="true"
        style={{ width: dot, height: dot, margin: `0 ${mx}px` }} />
      KAY
    </Tag>
  );
}

function WordmarkSubtitle({ scale = 1 }) {
  const fs = 13 * scale;
  // D2.1 spec (May 26, 2026): dot 6.2px, r 1.35px, margin 0 2.25 0 0.5.
  // Was 8.5/2/3-1 — read too heavy against Space Mono cap height.
  const dot = 6.2 * scale;
  const r = 1.35 * scale;
  const mr = 2.25 * scale;
  const ml = 0.5 * scale;
  const dotStyle = {
    width: dot, height: dot,
    borderRadius: r,
    margin: `0 ${mr}px 0 ${ml}px`,
  };
  return (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      fontFamily: 'var(--font-mono)',
      fontSize: fs,
      fontWeight: 400,
      letterSpacing: '0.28em',
      color: 'var(--ink)',
    }}>
      <span>S</span><span>T</span>
      <span className="jmk-d" style={dotStyle} />
      <span>R</span><span>Y</span>
      <span style={{ width: 20 }} />
      <span>P</span><span>R</span>
      <span className="jmk-d" style={dotStyle} />
      <span>D</span><span>U</span><span>C</span><span>E</span><span>R</span>
    </div>
  );
}

window.Wordmark = Wordmark;
window.WordmarkSubtitle = WordmarkSubtitle;
