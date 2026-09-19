/**
 * TypeRise SVG Performance Charts Renderer
 * Ultra-lightweight, zero-dependency data visualizer for WPM & Accuracy trends.
 */

function renderSvgLineChart(containerId, labels, data, options = {}) {
  const container = document.getElementById(containerId);
  if (!container) return;

  if (!data || data.length === 0) {
    container.innerHTML = `<div style="text-align:center; padding: 3rem; color: var(--text-muted);">No practice sessions recorded yet. Start typing to build your history!</div>`;
    return;
  }

  const width = container.clientWidth || 600;
  const height = options.height || 220;
  const padding = 40;

  const minVal = options.min !== undefined ? options.min : Math.min(...data);
  const maxVal = options.max !== undefined ? options.max : Math.max(...data);
  const range = (maxVal - minVal) || 1;

  const strokeColor = options.color || '#3b82f6';
  const fillColor = options.fillColor || 'rgba(59, 130, 246, 0.1)';

  // Compute points
  const stepX = (width - padding * 2) / Math.max(1, data.length - 1);
  const points = data.map((val, idx) => {
    const x = padding + (idx * stepX);
    const normalizedY = (val - minVal) / range;
    const y = (height - padding) - (normalizedY * (height - padding * 2));
    return { x, y, val, label: labels[idx] || '' };
  });

  // Build SVG Path
  let pathD = `M ${points[0].x} ${points[0].y}`;
  for (let i = 1; i < points.length; i++) {
    pathD += ` L ${points[i].x} ${points[i].y}`;
  }

  // Area Fill Path
  const areaD = `${pathD} L ${points[points.length - 1].x} ${height - padding} L ${points[0].x} ${height - padding} Z`;

  // Build Dots & Tooltips
  let dotsSvg = '';
  points.forEach((p) => {
    dotsSvg += `
      <circle cx="${p.x}" cy="${p.y}" r="4" fill="${strokeColor}" stroke="#ffffff" stroke-width="2">
        <title>${p.label}: ${p.val}</title>
      </circle>
    `;
  });

  // Grid Lines
  const gridY1 = height - padding;
  const gridYMid = height / 2;
  const gridYTop = padding;

  const svgHtml = `
    <svg width="100%" height="${height}" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" style="overflow: visible;">
      <!-- Grid Lines -->
      <line x1="${padding}" y1="${gridYTop}" x2="${width - padding}" y2="${gridYTop}" stroke="var(--border)" stroke-dasharray="4" />
      <line x1="${padding}" y1="${gridYMid}" x2="${width - padding}" y2="${gridYMid}" stroke="var(--border)" stroke-dasharray="4" />
      <line x1="${padding}" y1="${gridY1}" x2="${width - padding}" y2="${gridY1}" stroke="var(--border)" />

      <!-- Y Axis Labels -->
      <text x="${padding - 8}" y="${gridYTop + 4}" fill="var(--text-subtle)" font-size="11" text-anchor="end" font-family="var(--font-mono)">${Math.round(maxVal)}</text>
      <text x="${padding - 8}" y="${gridYMid + 4}" fill="var(--text-subtle)" font-size="11" text-anchor="end" font-family="var(--font-mono)">${Math.round((maxVal + minVal) / 2)}</text>
      <text x="${padding - 8}" y="${gridY1 + 4}" fill="var(--text-subtle)" font-size="11" text-anchor="end" font-family="var(--font-mono)">${Math.round(minVal)}</text>

      <!-- Fill & Line -->
      <path d="${areaD}" fill="${fillColor}" />
      <path d="${pathD}" fill="none" stroke="${strokeColor}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />

      <!-- Data Dots -->
      ${dotsSvg}
    </svg>
  `;

  container.innerHTML = svgHtml;
}

window.renderSvgLineChart = renderSvgLineChart;
